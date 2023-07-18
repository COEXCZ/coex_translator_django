import json
from unittest import mock

from django.core.cache import caches
from django.conf import settings
from django.test import TestCase
from django.utils.translation import gettext, activate as activate_lang

from coex_translator.app_settings import app_settings
from coex_translator.internal import constants
from coex_translator.internal.clients import TranslatorClient
from coex_translator.internal.clients.translator.schemas import TranslationResponseSchema, \
    TranslationResponseMessageSchema
from coex_translator.internal.services import translation_refresh
from coex_translator.internal.storage import S3Storage
from coex_translator.service import TranslationService

cache = caches[settings.DJANGO_CACHE_TRANSLATIONS]


class TranslationRefreshServiceTestCase(TestCase):
    def setUp(self):
        self.service = translation_refresh.TranslationRefreshService()
        self.language = "en"
        self.translation = {"hello-world": "Hello world"}

        # Translation as would-be downloaded from the storage.
        self.translation_as_download = bytes(json.dumps(self.translation).encode('utf-8'))
        # Translation as would-be returned by the Translator service.
        self.translation_as_translator_resp = TranslationResponseSchema(
            id=1,
            message=TranslationResponseMessageSchema(
                id=1,
                key=list(self.translation.keys())[0],
            ),
            language=self.language,
            translation=list(self.translation.values())[0],
        )

        activate_lang(self.language)

    def tearDown(self) -> None:
        TranslationService().clear()

    def test_refresh_translations_from_the_storage_json_file(self):
        # Check that the message is not translated yet.
        self._check_is_translated(False)

        with mock.patch.object(S3Storage, 'download', return_value=self.translation_as_download) as download_mock:
            with mock.patch.object(TranslatorClient, 'fetch_translations') as translator_service_call_mock:
                self.service.refresh_translations(languages=[self.language])
        download_mock.assert_called_once_with(
            f"{app_settings['STORAGE']['FOLDER']}/"
            f"{settings.ENVIRONMENT}/"
            f"{constants.APP_NAME}/"
            f"{self.language}/"
            f"translations.json"
        )
        translator_service_call_mock.assert_not_called()  # should be called only as a backup if the storage fails
        self._check_is_translated()

    def test_refresh_translations_from_the_translator_service_if_storage_download_fails(self):
        # Check that the message is not translated yet.
        self._check_is_translated(False)

        with mock.patch.object(S3Storage, 'download', side_effect=S3Storage.ConnectionError) as download_mock:
            with mock.patch.object(
                    TranslatorClient,
                    'fetch_translations',
                    return_value=[self.translation_as_translator_resp],
            ) as translator_service_call_mock:
                self.service.refresh_translations(languages=[self.language])
        download_mock.assert_called_once()
        translator_service_call_mock.assert_called_once_with(language=self.language)
        self._check_is_translated()

    def test_raises_exception_if_both_storage_and_translator_service_fail(self):
        self._check_is_translated(False)

        with mock.patch.object(S3Storage, 'download', side_effect=S3Storage.ConnectionError) as download_mock:
            with mock.patch.object(TranslatorClient, 'fetch_translations', side_effect=Exception) as translator_mock:
                with self.assertRaises(Exception):  # TODO maybe create a custom exception for this case?
                    self.service.refresh_translations(languages=[self.language])
        download_mock.assert_called_once()
        translator_mock.assert_called_once()
        self._check_is_translated(False)

    def _check_is_translated(self, expected: bool = True, key: str = None):
        if key is None:
            key = list(self.translation.keys())[0]
        exp_value = list(self.translation.values())[0] if expected else key
        self.assertEqual(gettext(key), exp_value)

