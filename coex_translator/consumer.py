import logging
from pathlib import Path

from coex_translator.app_settings import app_settings

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

        if body == TranslationAMQPPublisher.TRANSLATION_UPDATE_MESSAGE:
            if self.daemon:  # TODO is this check good enough? Maybe distinguish by some ENV variable?
                # Docker SWARM case
                # This is a daemon thread running in the background of main app container worker process.
                # We need to directly refresh translations cache.
                # TODO fetch new translations from storage, fallback to coex translator API if storage is unavailable and rewrite translation cache
                # move this logic to some appropriate module
                pass
            else:
                # K8s case
                # This is a thread running in the sidecar container.
                # Notify uvicorn in the main app container through volume to restart and fetch new translations.
                Path(app_settings["UVICORN_RELOAD_FILE_PATH"]).touch()
        else:
            logger.error('Translation consumer received unknown message', extra={'message_body': body})
