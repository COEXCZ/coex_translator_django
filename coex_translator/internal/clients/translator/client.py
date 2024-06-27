import typing

import requests

from coex_translator.app_settings import app_settings
from coex_translator.internal import constants
from coex_translator.internal.clients import base
from coex_translator.internal.clients.translator import schemas


class TranslatorClient(base.BaseAuthHttpClient):  # TODO set up auth token?
    base_url: typing.ClassVar[str] = app_settings["API_BASE_URL"]
    default_token: typing.ClassVar[str] = app_settings['API_TOKEN']

    def fetch_translations(
            self,
            translated: bool = True,
            language: str = None,
            app_name: str = constants.BE_APP_NAME,
    ) -> list[schemas.TranslationResponseSchema]:
        resp: requests.Response = self._send_get_request(
            url=f"{self.base_url}/translation",
            data=schemas.TranslationsRequestFilterSchema(
                is_translated=translated,
                language=language,
                limit=999999,
                app_name=app_name,
            ).dict()
        )
        return [schemas.TranslationResponseSchema.build(d) for d in resp.json().get('items', [])]

    def export_messages(
            self,
            message_ids: list[str],
            branch_name: str,
            tag_id: str = None,
            commit_id: str = None,
    ) -> None:
        """
        Export message keys to the Translator service.

        :param message_ids: List of message keys ("msg_id" in po files).
        :param branch_name: Name of the git branch from which the messages are exported.
        :param tag_id: ID of the git tag from which the messages are exported.
        :param commit_id: ID of the git commit from which the messages are exported.
        """
        resp: requests.Response = self._send_post_request(
            url=f"{self.base_url}/message/import/",
            data=schemas.ExportMessagesRequestSchema(
                messages={msg: None for msg in message_ids},  # None is the default translation (We don't have it on BE)
                meta=schemas.ExportMessagesMetaSchema(
                    branch_name=branch_name,
                    tag_id=tag_id,
                    commit_id=commit_id,
                ),
            ).dict(),
        )

    def publish_translations(self, environment: str) -> schemas.PublishTranslationsResponseSchema:
        """
        Publish translations for given environment.

        :param environment: Name of the environment.
        """
        resp: requests.Response = self._send_post_request(
            url=f"{self.base_url}/translation/publish",
            data=schemas.PublishTranslationsRequestSchema(
                environments=[environment],
                app_name=constants.BE_APP_NAME,
            ).dict(),
        )

        return schemas.PublishTranslationsResponseSchema.build(resp.json())
