import dataclasses
import json

import requests


@dataclasses.dataclass
class HttpClientException(Exception):
    message: str = "HTTP Client error."
    response: requests.Response | None = None

    @property
    def response_data(self) -> dict | str | None:
        if self.response is None:
            return None
        try:
            return self.response.json()
        except json.JSONDecodeError:
            return str(self.response)
