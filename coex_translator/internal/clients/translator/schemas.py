import dataclasses

import typing
from django.conf import settings

from coex_translator.internal.clients import base


@dataclasses.dataclass(kw_only=True)
class TranslationsRequestFilterSchema(base.ClientRequestDataSchema):
    """GET params used for filtering the translations in the Translator service."""
    key: str = None
    is_translated: bool = None
    language: str = None  # language code
    app_name: str = settings.PROJECT_NAME
    environment: str = settings.ENVIRONMENT
    offset: int = 0
    limit: int = 100


@dataclasses.dataclass(kw_only=True)
class TranslationResponseMessageSchema:
    key: str
    id: int

    @classmethod
    def build(cls, data: dict) -> typing.Self:
        return cls(
            key=data['key'],
            id=data['id'],
        )


@dataclasses.dataclass(kw_only=True)
class TranslationResponseSchema(base.ClientResponseDataSchema):
    id: int
    message: TranslationResponseMessageSchema
    language: str  # language code
    translation: str | None

    @classmethod
    def build(cls, data: dict) -> typing.Self:
        return cls(
            id=data['id'],
            message=TranslationResponseMessageSchema.build(data['message']),
            language=data['language'],
            translation=data['translation'],
        )