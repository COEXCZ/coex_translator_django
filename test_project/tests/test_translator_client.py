import dataclasses
from unittest import mock

from django.conf import settings
from django.test import TestCase

from coex_translator.internal.clients import TranslatorClient
from test_project.tests.utils import load_fixture


@dataclasses.dataclass
class MockResponse:
    data: dict | list | str
    status_code: int = 200

    def json(self) -> dict:
        return self.data


class TranslatorClientTestCase(TestCase):
    def setUp(self):
        self.trans_client = TranslatorClient()

    def test_fetch_translations(self):
        fixture_data: list[dict] = load_fixture('translator/translation_response.json')
        mock_resp = MockResponse(data=fixture_data)
        with mock.patch('requests.request', return_value=mock_resp) as request_mock:
            translations = self.trans_client.fetch_translations()
            request_mock.assert_called_once_with(
                'get',
                url=f"{settings.COEX_TRANSLATOR_API_BASE_URL}/translation",
                json={},
                headers={
                    'X-Authorization': f'Bearer {self.trans_client.token}',
                },
                params={
                    'is_translated': True,
                    'language': None,
                    'limit': 999999,
                    'app_name': settings.PROJECT_NAME,
                    'environment': settings.ENVIRONMENT,
                },
            )

        self.assertEqual(len(translations), len(fixture_data))

    def test_fetch_translations_bad_response_raises_the_client_exception(self):
        mock_resp = MockResponse(data="Bad response", status_code=400)
        with mock.patch.object(self.trans_client, '_send_get_request', return_value=mock_resp):
            with self.assertRaises(self.trans_client.exception_cls):
                self.trans_client.fetch_translations()

    # TODO test invalid format of the response

