import json
import typing


def load_fixture(path: str) -> typing.Any:
    base_path = 'test_project/tests/fixtures'
    if not path.startswith(base_path):
        path = f'{base_path}/{path}'
    with open(path, 'r') as f:
        return json.load(f)
