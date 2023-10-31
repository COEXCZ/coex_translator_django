import typing
from django.conf import settings as django_settings

SETTINGS_NAME: str = "COEX_TRANSLATOR"


class CoexTranslatorSettings(typing.TypedDict):
    """Settings of the CoexTranslator app."""
    API_BASE_URL: str  # URL to the Translator service API
    API_TOKEN: str
    UVICORN_RELOAD_FILE_PATH: typing.NotRequired[str]
    STARTUP_REFRESH_ENABLED: bool  # If True -> when app is reloaded, refresh translations
    FETCH_WITH_FE: bool
    AMQP: "_AMQPSettings"
    STORAGE: "_StorageSettings"


class _AMQPSettings(typing.TypedDict):
    """Settings of the AMQP broker."""
    CONSUMER_DAEMON_ENABLED: bool
    BROKER_URL: str
    QUEUE_PREFIX: str
    EXCHANGE: str
    ROUTING_KEY: str


class _StorageSettings(typing.TypedDict):
    """Settings of the object storage where files with translations are stored."""
    ACCESS_KEY_ID: str
    SECRET_ACCESS_KEY: str
    REGION_NAME: str
    ENDPOINT_URL: str
    BUCKET_NAME: str
    FOLDER: str  # Folder in the bucket where files with translations are stored


# Intercepting/loading and using this app's settings like this allows us to set default values for some settings
# if we ever want that or perform some checks on them.
app_settings: "CoexTranslatorSettings" = getattr(django_settings, SETTINGS_NAME, {})
