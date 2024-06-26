import dataclasses
from unittest import mock

from django.conf import settings
from django.test import TestCase

from coex_translator.app_settings import app_settings
from coex_translator.internal import constants
from coex_translator.internal.clients import TranslatorClient
from test_project.tests.utils import load_fixture


@dataclasses.dataclass
class MockResponse:
    data: dict | list | str
    status_code: int = 200

    def json(self) -> dict:
        return self.data

    @property
    def text(self) -> str:
        return str(self.data)

    @property
    def ok(self) -> bool:
        return self.status_code < 400


class TranslatorClientTestCase(TestCase):
    def setUp(self):
        self.trans_client = TranslatorClient()

    def test_fetch_translations(self):
        fixture_data: list[dict] = load_fixture('translator_service/translations_response.json')
        mock_resp = MockResponse(data=fixture_data)
        with mock.patch('requests.request', return_value=mock_resp) as request_mock:
            translations = self.trans_client.fetch_translations()
            request_mock.assert_called_once_with(
                'get',
                url=f"{app_settings['API_BASE_URL']}/translation",
                json={},
                headers={
                    'X-Authorization': f'Bearer {self.trans_client.token}',
                },
                params={
                    'is_translated': True,
                    'limit': 999999,
                    'offset': 0,
                    'app_name': constants.BE_APP_NAME,
                    'environment': settings.ENVIRONMENT,
                },
                timeout=TranslatorClient.timeout
            )

        self.assertEqual(len(translations), len(fixture_data))

    def test_fetch_translations_bad_response_raises_the_client_exception(self):
        mock_resp = MockResponse(data="Bad response", status_code=400)
        with mock.patch('requests.request', return_value=mock_resp):
            with self.assertRaises(self.trans_client.exception_cls):
                self.trans_client.fetch_translations()

    def test_publish_translations(self):
        fixture_data: list[dict] = load_fixture('translator_service/publish_translations_response.json')
        mock_resp = MockResponse(data=fixture_data)
        with mock.patch('requests.request', return_value=mock_resp) as request_mock:
            publish_results = self.trans_client.publish_translations('testing')
            request_mock.assert_called_once_with(
                'post',
                url=f"{app_settings['API_BASE_URL']}/translation/publish",
                json={
                    'environments': ['testing'],
                    'app_name': constants.BE_APP_NAME
                },
                headers={
                    'X-Authorization': f'Bearer {self.trans_client.token}',
                },
                params={},
                timeout=TranslatorClient.timeout
            )

            self.assertEqual(len(publish_results.items), len(fixture_data['items']))

    def test_client_default_token_set_on_instance(self):
        client = TranslatorClient()
        self.assertEqual(client.token, app_settings['API_TOKEN'])

    def test_client_custom_token_set_on_instance(self):
        client = TranslatorClient(token="CUSTOM_TOKEN")
        self.assertEqual(client.token, "CUSTOM_TOKEN")
