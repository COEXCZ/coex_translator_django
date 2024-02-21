# COex Translator Django

Django app handling integration of COex Translator.

## Installation

Install package

```shell
pip install git+ssh://git@github.com/COEXCZ/coex_translator_django.git
# or
poetry add git+ssh://git@github.com/COEXCZ/coex_translator_django.git
```

## Configuration

### Django settings

Add coex_translator to `INSTALLED_APPS`.

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'coex_translator',
]
```

Setup in memory cache for translations.

```python
DJANGO_CACHE_TRANSLATIONS = 'translations'
CACHES = {
    DJANGO_CACHE_TRANSLATIONS: {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        'LOCATION': '{}:{}:{}'.format(PROJECT_NAME, ENVIRONMENT, DJANGO_CACHE_TRANSLATIONS),
        'TIMEOUT': None,
        'KEY_PREFIX': '{}:{}:{}'.format(PROJECT_NAME, ENVIRONMENT, DJANGO_CACHE_TRANSLATIONS)
    }
}
```

## include urls

```python
from django.urls import include, path

urlpatterns = [
    ...
    path('coex-translator/', include('coex_translator.urls')),
]
```

## Deployment

### Settings
The settings are namespaced under `COEX_TRANSLATOR` key.

Settings example:
```python
import typing
import os

from decouple import AutoConfig, Csv

if typing.TYPE_CHECKING:
    from coex_translator.app_settings import CoexTranslatorSettings

config = AutoConfig(os.environ.get("DJANGO_CONFIG_ENV_DIR"))

PROJECT_NAME = config('PROJECT_NAME', default='coex_translator')


...


COEX_TRANSLATOR: "CoexTranslatorSettings" = {
    "API_BASE_URL": config('COEX_TRANSLATOR_API_BASE_URL', default=''),
    "API_TOKEN": config('COEX_TRANSLATOR_API_TOKEN', default=''),
    "UVICORN_RELOAD_FILE_PATH": config('COEX_TRANSLATOR_UVICORN_RELOAD_FILE_PATH', default=''),
    "STARTUP_REFRESH_ENABLED": config('COEX_TRANSLATOR_STARTUP_REFRESH_ENABLED', default=False, cast=bool),
    "DISABLE_IN_MANAGEMENT_COMMANDS": config('COEX_TRANSLATOR_DISABLE_IN_MANAGEMENT_COMMANDS', default=False, cast=bool),
    'WEBHOOK_SECRET': config('COEX_TRANSLATOR_WEBHOOK_SECRET', default=''),
    "AMQP": {
        "BROKER_URL": config('COEX_TRANSLATOR_AMQP_BROKER_URL', default=f"amqp://{PROJECT_NAME}:{PROJECT_NAME}@rabbitmq/{PROJECT_NAME}"),
        "QUEUE_PREFIX": config('COEX_TRANSLATOR_AMQP_QUEUE_PREFIX', default='translation'),
        "EXCHANGE": config('COEX_TRANSLATOR_AMQP_EXCHANGE', default='translation'),
        "ROUTING_KEY": config('COEX_TRANSLATOR_AMQP_ROUTING_KEY', default='translation'),
        "CONSUMER_DAEMON_ENABLED": config('COEX_TRANSLATOR_AMQP_CONSUMER_DAEMON_ENABLED', default=False, cast=bool),
        "CONNECTION_RETRY_COUNTDOWN": config('COEX_TRANSLATOR_AMQP_CONNECTION_RETRY_COUNTDOWN', default='1,10,100', cast=Csv(int)),
    },
    "STORAGE": {
        "ACCESS_KEY_ID": config('COEX_TRANSLATOR_STORAGE_ACCESS_KEY_ID', default=''),
        "SECRET_ACCESS_KEY": config('COEX_TRANSLATOR_STORAGE_SECRET_ACCESS_KEY', default=''),
        "REGION_NAME": config('COEX_TRANSLATOR_STORAGE_REGION_NAME', default=''),
        "ENDPOINT_URL": config('COEX_TRANSLATOR_STORAGE_ENDPOINT_URL', default=''),
        "BUCKET_NAME": config('COEX_TRANSLATOR_STORAGE_BUCKET_NAME', default=''),
        "FOLDER": config('COEX_TRANSLATOR_STORAGE_FOLDER', default=''),
    }
}

...
```
For up-to-date available settings, see [CoexTranslatorSettings](coex_translator/app_settings.py), or their
usage in the [test_project](test_project/settings.py).

### for k8s deployment (default):  
 
Setup translation AMQP consumer in pod sidecar container.

```diff
python manage.py translation_amqp_consumer
```

Setup uvicorn worker with `--reload-dir <path>` option. https://www.uvicorn.org/settings/#development

```diff
uvicorn worker <app> --reload-dir <path>
```

and set

```diff
COEX_TRANSLATOR['UVICORN_RELOAD_FILE_PATH'] = "<path>/__init__.py"
```

translation AMQP consumer will touch this file when new version is published from COex Translator.

### for other deployments (Docker SWARM):  

```diff
 COEX_TRANSLATOR['AMQP']['CONSUMER_DAEMON_ENABLED'] = True
```

This will start translation AMQP consumer daemon in background of main worker process.
Consumer will fetch and set new translations in cache when new version is published from COex Translator.

```diff
COEX_TRANSLATOR['STARTUP_REFRESH_ENABLED']['CONSUMER_DAEMON_ENABLED'] = True
```
To enable translations refresh on app worker startup.

> **Warning**  
> To ensure that translations work properly even on Model class variables (e.g. `Meta.verbose_name`), call 
> `coex_translator.gettext.monkeypatch_translations()` in the project's root `__init__.py` file.


## Contribution

Install with dev dependencies

```shell
poetry install --with dev
```
