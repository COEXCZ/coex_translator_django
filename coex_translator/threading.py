import threading

import pika
import pika.channel
import pika.exchange_type

import socket


class ThreadedAMPQConsumer(threading.Thread):
    QUEUE_PREFIX: str = NotImplemented
    BROKER_URL: str = NotImplemented
    EXCHANGE: str = NotImplemented
    ROUTING_KEY: str = NotImplemented

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        parameters = pika.URLParameters(self.BROKER_URL)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        queue_name = f'{self.QUEUE_PREFIX}{socket.gethostname()}'
        self.channel.queue_declare(queue=queue_name, auto_delete=True)
        self.channel.exchange_declare(
            exchange=self.EXCHANGE,
            exchange_type=pika.exchange_type.ExchangeType.direct,
            passive=True,
            auto_delete=True
        )
        self.channel.queue_bind(queue=queue_name, exchange=self.EXCHANGE, routing_key=self.ROUTING_KEY)
        self.channel.basic_consume(queue_name, on_message_callback=self.callback)

    def on_message(self, body: bytes):
        raise NotImplementedError()

    def callback(self, channel: pika.channel.Channel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes):
        self.on_message(body)
        channel.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        self.channel.start_consuming()
