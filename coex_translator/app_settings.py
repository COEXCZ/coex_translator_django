from typing import TypedDict
from django.conf import settings as django_settings

SETTINGS_NAME: str = "COEX_TRANSLATOR"


class CoexTranslatorSettings(TypedDict, total=False):
    """Settings of the CoexTranslator app."""
    API_BASE_URL: str  # URL to the Translator service API
    UVICORN_RELOAD_FILE_PATH: str
    STARTUP_REFRESH_ENABLED: bool  # If True -> when app is reloaded, refresh translations
    AMQP: "_AMQPSettings"
    STORAGE: "_StorageSettings"


class _AMQPSettings(TypedDict, total=False):
    """Settings of the AMQP broker."""
    CONSUMER_DAEMON_ENABLED: bool
    BROKER_URL: str
    QUEUE_PREFIX: str
    EXCHANGE: str
    ROUTING_KEY: str


class _StorageSettings(TypedDict, total=False):
    """Settings of the object storage where files with translations are stored."""
    ACCESS_KEY_ID: str
    SECRET_ACCESS_KEY: str
    REGION_NAME: str
    ENDPOINT_URL: str
    BUCKET_NAME: str
    FOLDER: str  # Folder in the bucket where files with translations are stored


def _deep_update(source: dict, overrides: dict) -> dict:
    """
    Update a nested dictionary. Modify `source` in place.
    """
    for key, value in overrides.items():
        if isinstance(value, dict) and value:
            source[key] = _deep_update(source.get(key, {}), value)
        else:
            source[key] = overrides[key]
    return source


def _load_with_defaults() -> "CoexTranslatorSettings":
    translator_settings: "CoexTranslatorSettings" = getattr(django_settings, SETTINGS_NAME, {})

    defaults: "CoexTranslatorSettings" = {
        "STARTUP_REFRESH_ENABLED": False,
        "AMQP": {
            "CONSUMER_DAEMON_ENABLED": False,
            "QUEUE_PREFIX": "translation",
            "EXCHANGE": "translation",
            "ROUTING_KEY": "translation",
        },
        "STORAGE": {
            "FOLDER": "translations",
        },
    }
    _deep_update(translator_settings, defaults)
    return translator_settings


app_settings: "CoexTranslatorSettings" = _load_with_defaults()
