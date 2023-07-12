import logging
from pathlib import Path

from coex_translator.app_settings import app_settings
from coex_translator.internal.services.translation_refresh import TranslationRefreshService

from coex_translator.threading import ThreadedAMPQConsumer
from coex_translator.publisher import TranslationAMQPPublisher

logger = logging.getLogger(__name__)


class ThreadedTranslationAMQPConsumer(ThreadedAMPQConsumer):
    BROKER_URL: str = app_settings["AMQP"]["BROKER_URL"]
    QUEUE_PREFIX: str = app_settings["AMQP"]["QUEUE_PREFIX"]
    EXCHANGE: str = app_settings["AMQP"]["EXCHANGE"]
    ROUTING_KEY: str = app_settings["AMQP"]["ROUTING_KEY"]

    def on_message(self, body: bytes):
        body = body.decode('utf-8')

        if body != TranslationAMQPPublisher.TRANSLATION_UPDATE_MESSAGE:
            logger.error('Translation consumer received unknown message', extra={'message_body': body})
            return

        logger.info('Translation consumer received translation update message', extra={'message_body': body})
        if app_settings['AMQP']['CONSUMER_DAEMON_ENABLED']:
            # Docker SWARM case #################################
            # This is a daemon thread running in the background of the main app container worker process.
            # We need to directly refresh translations cache.
            logger.info('Using daemon thread to refresh translations')
            TranslationRefreshService().refresh_translations()
        else:
            # K8s case ##########################################
            # This is a thread running in the sidecar container.
            # Notify uvicorn in the main app container through volume to restart and fetch new translations.
            logger.info('Using file touch to refresh translations')
            Path(app_settings["UVICORN_RELOAD_FILE_PATH"]).touch()
