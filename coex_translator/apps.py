from django.apps import AppConfig


class CoexTranslatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'coex_translator'

    def ready(self):
        from .translation import monkeypatch_translations

        monkeypatch_translations()
