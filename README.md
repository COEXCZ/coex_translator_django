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

```diff
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

```diff
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

Set COex Translator API base URL.

```diff
COEX_TRANSLATOR_API_BASE_URL = config('COEX_TRANSLATOR_API_BASE_URL', default='')
```

Set AMQP broker url.

```diff
COEX_TRANSLATOR_AMQP_BROKER_URL = config('COEX_TRANSLATOR_AMQP_BROKER_URL', default='')
```

## Deployment

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
COEX_TRANSLATOR_UVICORN_RELOAD_FILE_PATH = <path>/__init__.py
```

translation AMQP consumer will touch this file when new version is published from COex Translator.

### for other deployments (Docker SWARM):  

```diff
 TRANSLATION_AMQP_CONSUMER_DAEMON_ENABLED = True
```

This will start translation AMQP consumer daemon in background of main worker process.
Consumer will fetch and set new translations in cache when new version is published from COex Translator.

## Contribution

Install with dev dependencies

```shell
poetry install --with dev
```
