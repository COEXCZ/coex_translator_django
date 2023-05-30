import dataclasses

from django.conf import settings

from coex_translator._utils.clients import base


@dataclasses.dataclass(kw_only=True)
class TranslationsRequestFilterSchema(base.ClientRequestDataSchema):
    """GET params used for filtering the translations in the Translator service."""
    key: str = None
    is_translated: bool = None
    language: str = None  # language code
    app_name: str = settings.PROJECT_NAME
    environment: str = settings.ENVIRONMENT  # TODO add this filter in the translator app
    offset: int = 0
    limit: int = 100


@dataclasses.dataclass(kw_only=True)
class TranslationResponseSchema(base.ClientResponseDataSchema):
    @dataclasses.dataclass(kw_only=True)
    class Message:
        key: str
        id: int

    id: int
    message: Message
    language: str  # language code
    translation: str | None
