import atexit
import sys

from django.apps import AppConfig

from coex_translator.app_settings import app_settings
from coex_translator.internal.services.translation_refresh import TranslationRefreshService


class CoexTranslatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coex_translator'

    def ready(self):
        from coex_translator.consumer import ThreadedTranslationAMQPConsumer
        from coex_translator.gettext import monkeypatch_translations

        monkeypatch_translations()

        if app_settings["AMQP"]["CONSUMER_DAEMON_ENABLED"]:
            translation_consumer = ThreadedTranslationAMQPConsumer(daemon=True)
            translation_consumer.start()

            #  To gracefully stop daemon thread on exit (close connection to AMQP broker)
            atexit.register(translation_consumer.stop)

        if 'manage.py' not in sys.argv and app_settings["STARTUP_REFRESH_ENABLED"]:
            #  Refresh translations on startup only for workers (uwsgi, gunicorn, etc.)
            TranslationRefreshService().refresh_translations()
