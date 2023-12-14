import threading
import logging

from time import sleep

import pika
import pika.channel
import pika.exchange_type
import pika.exceptions
import pika.frame

import socket


logger = logging.getLogger(__name__)


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
        self._retries = 0

    def on_connection_open(self, connection):
        self._connection = connection
        self._connection.channel(on_open_callback=self.on_channel_open)
        self._retries = 0

    def _retry_connect(self, connection_error: pika.exceptions.AMQPError):
        if self._retries > 3:
            raise Exception("Too many retries") from connection_error

        countdown = 1 * (10**self._retries)  # (1, 10, 100)

        logger.warning("AMQP Connection error, retrying",
                       extra={'countdown': countdown, 'retries': self._retries, 'error': str(connection_error)})
        sleep(countdown)

        self._retries += 1
        self.connect()

    def on_connection_closed(self, connection: pika.SelectConnection, reason: pika.exceptions.AMQPConnectionError):
        self._connection = None
        self._channel = None
        self._retry_connect(reason)

    def on_connection_error(self, connection: pika.SelectConnection, error: pika.exceptions.AMQPError):
        self._retry_connect(error)

    def on_channel_open(self, channel):
        self._channel = channel
        self._channel.add_on_close_callback(self.on_channel_closed)
        self._channel.exchange_declare(
            exchange=self.EXCHANGE,
            auto_delete=True,
            callback=self.on_exchange_declareok,
        )

    def on_channel_closed(self, channel: pika.channel.Channel, reason: pika.exceptions.AMQPChannelError):
        try:
            self._connection.close()
        except pika.exceptions.ConnectionWrongStateError:
            #  Connection is already closed
            pass

    def on_exchange_declareok(self, method_frame: pika.frame.Method):
        self._channel.queue_declare(queue=self.queue_name, auto_delete=True, callback=self.on_queue_declareok)

    def on_queue_declareok(self, method_frame: pika.frame.Method):
        try:
            self._channel.queue_bind(queue=self.queue_name, exchange=self.EXCHANGE, routing_key=self.ROUTING_KEY)
        except pika.exceptions.ChannelWrongStateError as e:
            #  Channel is already closing or is not opened yet
            self._retry_connect(e)
        else:
            self._channel.basic_consume(self.queue_name, on_message_callback=self.callback)

    def on_message(self, body: bytes):
        raise NotImplementedError()

    def callback(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver,
                 properties: pika.spec.BasicProperties, body: bytes):
        self.on_message(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def connect(self):
        parameters = pika.URLParameters(self.BROKER_URL)
        self._connection = pika.SelectConnection(
            parameters,
            on_open_callback=self.on_connection_open,
            on_close_callback=self.on_connection_closed,
            on_open_error_callback=self.on_connection_error
        )
        self._connection.ioloop.start()

    def run(self):
        self.connect()

    def stop(self):
        if not self._connection:
            #  Connection is already closed
            return

        if self._channel:
            self._channel.close()
        self._connection.ioloop.stop()
