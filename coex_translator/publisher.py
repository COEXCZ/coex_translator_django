import pika
import logging

from coex_translator.app_settings import app_settings

logger = logging.getLogger(__name__)


class TranslationAMQPPublisher:
    TRANSLATION_UPDATE_MESSAGE = 'translations_published'

    @classmethod
    def publish_update_translations(cls):
        #  This method is prepared for future use in webhooks received from COex translator
        logger.debug("Sending translations update command.")

        body = cls.TRANSLATION_UPDATE_MESSAGE.encode('utf-8')

        cls._publish(body)

    @classmethod
    def _publish(cls, body: bytes):
        parameters = pika.URLParameters(app_settings["AMQP"]["BROKER_URL"])
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(
            app_settings["AMQP"]["EXCHANGE"],
            auto_delete=True
        )
        channel.basic_publish(
            app_settings["AMQP"]["EXCHANGE"],
            app_settings["AMQP"]["ROUTING_KEY"],
            body
        )
