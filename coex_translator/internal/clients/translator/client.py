import typing

import requests
from django.conf import settings

from coex_translator.internal.clients import base
from coex_translator.internal.clients.translator import schemas


class TranslatorClient(base.BaseAuthHttpClient):  # TODO set up auth token?
    base_url: typing.ClassVar[str] = settings.COEX_TRANSLATOR_API_BASE_URL

    def fetch_translations(
            self,
            translated: bool = True,
            language: str = None,
    ) -> list[schemas.TranslationResponseSchema]:
        resp: requests.Response = self._send_get_request(
            url=f"{self.base_url}/translation",
            data=schemas.TranslationsRequestFilterSchema(
                is_translated=translated,
                language=language,
                limit=999999,  # TODO allow limit=None in the Translator API?
            ).dict()
        )
        data = resp.json()
        return [schemas.TranslationResponseSchema(**d) for d in data]



