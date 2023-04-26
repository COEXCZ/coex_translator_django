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
+
+   'coex_translator',
]
```

Setup in memory cache for translations.

```diff
+ DJANGO_CACHE_TRANSLATIONS = 'translations'
CACHES = {
+    DJANGO_CACHE_TRANSLATIONS: {
+        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
+        'LOCATION': '{}:{}:{}'.format(PROJECT_NAME, ENVIRONMENT, DJANGO_CACHE_TRANSLATIONS),
+        'TIMEOUT': None,
+        'KEY_PREFIX': '{}:{}:{}'.format(PROJECT_NAME, ENVIRONMENT, DJANGO_CACHE_TRANSLATIONS)
+    }
}
```

Set COex Translator API base URL.

```diff
+ COEX_TRANSLATOR_API_BASE_URL = config('COEX_TRANSLATOR_API_BASE_URL', default='')
```

## Contribution

Install with dev dependencies

```shell
poetry install --with dev
```
