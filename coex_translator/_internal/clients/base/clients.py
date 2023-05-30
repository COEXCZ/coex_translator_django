import json
import logging

import typing
import uuid

import requests

from coex_translator._internal.clients.base import exceptions

logger = logging.getLogger(__name__)
HTTPMethodsType = typing.Literal['get', 'post', 'put', 'delete']


class BaseHttpClient:
    exception_cls: type[exceptions.HttpClientException] = exceptions.HttpClientException
    verbose_name: str = 'HTTP Client'

    def _send_post_request(self, url: str, data: dict) -> requests.Response:
        return self._send_request(method='post', url=url, data=data)

    def _send_put_request(self, url: str, data: dict) -> requests.Response:
        return self._send_request(method='put', url=url, data=data)

    def _send_delete_request(self, url: str, data: dict) -> requests.Response:
        return self._send_request(method='delete', url=url, data=data)

    def _send_get_request(self, url: str, data: dict | None = None) -> requests.Response:
        return self._send_request(method='get', url=url, params=data)

    def _get_headers(self, method: HTTPMethodsType, url: str, data: dict) -> dict[str, str]:
        return {}

    def _send_request(self, method: HTTPMethodsType, url: str, data: dict = None, params: dict = None) -> requests.Response:
        identifier = uuid.uuid4()

        if not data:
            data = {}
        if not params:
            params = {}

        try:
            logger.debug(f"Sending {method} request ({identifier}) to {url} with {data} and {params}")
            resp: requests.Response = requests.request(
                method,
                url=url,
                json=data,
                headers=self._get_headers(method=method, url=url, data=data),
                params=params,
            )
        except requests.ConnectionError as e:
            logger.error(f'Http Client API connection error, {e}', exc_info=True)
            raise self.exception_cls(f"{self} connection error", response=e.response)

        logger.debug(f"For request ({identifier}) received response {resp.status_code}")
        if resp.ok:
            return resp

        try:
            err_data = resp.json()
        except json.JSONDecodeError:
            err_data = {}
        logger.error(f'{self} error response', extra={
            'identifier': identifier,
            'err_data': err_data,
            'err_text': resp.text,
            'url': url,
            'data': data,
        })
        raise self.exception_cls(f"{self} error response {resp.status_code}", response=resp)

    def __str__(self) -> str:
        return self.__class__.__name__


class BaseAuthHttpClient(BaseHttpClient):
    default_token: str = None

    def __init__(self, token: str | None = None):
        if token is None:
            token = self.default_token
        self.token = token

    def _get_headers(self, method: HTTPMethodsType, url: str, data: dict) -> dict[str, str]:
        headers = super()._get_headers(method=method, url=url, data=data)
        return headers | {
            'X-Authorization': f'Bearer {self.token}',
        }
