import logging

from django.conf import settings

from coex_translator.threading import ThreadedAMPQConsumer
from coex_translator.translator import Translator, TRANSLATION_UPDATE_MESSAGE

logger = logging.getLogger(__name__)


class ThreadedTranslationAMQPConsumer(ThreadedAMPQConsumer):
    BROKER_URL: str = settings.COEX_TRANSLATOR_AMQP_BROKER_URL
    QUEUE_PREFIX: str = settings.COEX_TRANSLATOR_AMQP_QUEUE_PREFIX
    EXCHANGE: str = settings.COEX_TRANSLATOR_AMQP_EXCHANGE
    ROUTING_KEY: str = settings.COEX_TRANSLATOR_AMQP_ROUTING_KEY

    def on_message(self, body: bytes):
        body = body.decode('utf-8')

        if body == TRANSLATION_UPDATE_MESSAGE:
            Translator().update_translations()
        else:
            logger.error('Translation consumer received uknown message', extra={'message_body': body})
