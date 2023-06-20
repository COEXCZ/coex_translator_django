import json
from unittest import mock

from django.core.cache import caches
from django.conf import settings
from django.test import TestCase
from django.utils.translation import gettext, activate as activate_lang

from coex_translator.internal.clients import TranslatorClient
from coex_translator.internal.clients.translator.schemas import TranslationResponseSchema, \
    TranslationResponseMessageSchema
from coex_translator.internal.services import translation_refresh
from coex_translator.internal.storage import S3Storage

cache = caches[settings.DJANGO_CACHE_TRANSLATIONS]


class TranslationRefreshServiceTestCase(TestCase):
    def setUp(self):
        self.service = translation_refresh.TranslationRefreshService()
        self.translation = translation_refresh.Translation(
            message='hello-world',
            translation="Hello world",
            language='en',
        )

        # Translation as would-be downloaded from the storage.
        self.translation_as_download = bytes(json.dumps([self.translation.__dict__]).encode('utf-8'))
        # Translation as would-be returned by the Translator service.
        self.translation_as_translator_resp = TranslationResponseSchema(
            id=1,
            message=TranslationResponseMessageSchema(
                id=1,
                key=self.translation.message,
            ),
            language=self.translation.language,
            translation=self.translation.translation,
        )

        activate_lang(self.translation.language)

    def tearDown(self) -> None:
        cache.clear()

    def test_refresh_translations_from_the_storage_json_file(self):
        # Check that the message is not translated yet.
        self._check_is_translated(False)

        with mock.patch.object(S3Storage, 'download', return_value=self.translation_as_download) as download_mock:
            with mock.patch.object(TranslatorClient, 'fetch_translations') as translator_service_call_mock:
                self.service.refresh_translations(languages=[self.translation.language])
        download_mock.assert_called_once_with(
            f"{settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_FOLDER}/"
            f"{settings.ENVIRONMENT}/"
            f"{settings.PROJECT_NAME}/"
            f"{self.translation.language}/"
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
                self.service.refresh_translations(languages=[self.translation.language])
        download_mock.assert_called_once()
        translator_service_call_mock.assert_called_once_with(language=self.translation.language)
        self._check_is_translated()

    def test_raises_exception_if_both_storage_and_translator_service_fail(self):
        self._check_is_translated(False)

        with mock.patch.object(S3Storage, 'download', side_effect=S3Storage.ConnectionError) as download_mock:
            with mock.patch.object(TranslatorClient, 'fetch_translations', side_effect=Exception) as translator_mock:
                with self.assertRaises(Exception):  # TODO maybe create a custom exception for this case?
                    self.service.refresh_translations(languages=[self.translation.language])
        download_mock.assert_called_once()
        translator_mock.assert_called_once()
        self._check_is_translated(False)

    def _check_is_translated(self, expected: bool = True, key: str = None):
        if key is None:
            key = self.translation.message
        exp_value = self.translation.translation if expected else key
        self.assertEqual(gettext(self.translation.message), exp_value)

