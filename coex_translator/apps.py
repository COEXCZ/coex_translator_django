import atexit

from django.apps import AppConfig
from django.conf import settings


class CoexTranslatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coex_translator'

    def ready(self):
        from . import gettext
        from coex_translator.consumer import ThreadedTranslationAMQPConsumer

        if settings.TRANSLATION_AMQP_CONSUMER_DAEMON_ENABLED:
            translation_consumer = ThreadedTranslationAMQPConsumer(daemon=True)
            translation_consumer.start()

            #  To gracefully stop daemon thread on exit (close connection to AMQP broker)
            atexit.register(translation_consumer.stop)
