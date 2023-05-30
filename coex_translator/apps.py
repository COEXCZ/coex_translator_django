import atexit

from django.apps import AppConfig
from django.conf import settings

from coex_translator._internal.services.translation_refresh import TranslationRefreshService


class CoexTranslatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coex_translator'

    def ready(self):
        from coex_translator.consumer import ThreadedTranslationAMQPConsumer
        from coex_translator.gettext import monkeypatch_translations

        monkeypatch_translations()

        if settings.TRANSLATION_AMQP_CONSUMER_DAEMON_ENABLED:
            translation_consumer = ThreadedTranslationAMQPConsumer(daemon=True)
            translation_consumer.start()

            #  To gracefully stop daemon thread on exit (close connection to AMQP broker)
            atexit.register(translation_consumer.stop)

        TranslationRefreshService().refresh_translations()
