import pika
from django.conf import settings


class TranslationAMQPPublisher:

    @classmethod
    def publish(cls, body: bytes):
        parameters = pika.URLParameters(settings.TRANSLATION_AMQP_BROKER_URL)
        connection = pika.BlockingConnection(parameters)
        connection.channel().basic_publish(
            settings.TRANSLATIONS_AMQP_EXCHANGE,
            settings.TRANSLATIONS_AMQP_ROUTING_KEY,
            body
        )
