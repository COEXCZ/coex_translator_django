from django.apps import AppConfig


class CoexTranslatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coex_translator'

    def ready(self):
        from . import gettext
        from coex_translator.consumer import ThreadedTranslationAMQPConsumer

        translation_consumer = ThreadedTranslationAMQPConsumer(daemon=True)
        translation_consumer.start()

