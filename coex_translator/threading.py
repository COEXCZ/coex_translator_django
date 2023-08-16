import threading

import pika
import pika.channel
import pika.exchange_type
import pika.exceptions
import pika.frame

import socket


class ThreadedAMPQConsumer(threading.Thread):
    QUEUE_PREFIX: str = NotImplemented
    BROKER_URL: str = NotImplemented
    EXCHANGE: str = NotImplemented
    ROUTING_KEY: str = NotImplemented

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue_name = f"{self.QUEUE_PREFIX}.{socket.gethostname()}"
        self._connection = None
        self._channel = None

    def on_connection_open(self, connection):
        self._connection = connection
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.exchange_declare(
            exchange=self.EXCHANGE,
            auto_delete=True,
            callback=self.on_exchange_declareok,
        )

    def on_channel_closed(self, channel: pika.channel.Channel, reason: pika.exceptions.AMQPChannelError):
        self._connection.close()

    def on_exchange_declareok(self, method_frame: pika.frame.Method):
        self._channel.queue_declare(queue=self.queue_name, auto_delete=True, callback=self.on_queue_declareok)

    def on_queue_declareok(self, method_frame: pika.frame.Method):
        self._channel.queue_bind(queue=self.queue_name, exchange=self.EXCHANGE, routing_key=self.ROUTING_KEY)
        self._channel.basic_consume(self.queue_name, on_message_callback=self.callback)

    def on_message(self, body: bytes):
        raise NotImplementedError()

    def callback(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver,
                 properties: pika.spec.BasicProperties, body: bytes):
        self.on_message(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def connect(self):
        parameters = pika.URLParameters(self.BROKER_URL)
        self._connection = pika.SelectConnection(parameters, on_open_callback=self.on_connection_open)
        self._connection.ioloop.start()

    def run(self):
        self.connect()

    def stop(self):
        self._connection.ioloop.stop()
        if self._channel:
            self._channel.close()
