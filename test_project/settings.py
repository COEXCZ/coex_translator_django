"""
Django settings for test_project project.

Generated by 'django-admin startproject' using Django 4.2.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from decouple import AutoConfig, Csv

if TYPE_CHECKING:
    from coex_translator.app_settings import CoexTranslatorSettings

config = AutoConfig(os.environ.get("DJANGO_CONFIG_ENV_DIR"))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

PROJECT_NAME = config('PROJECT_NAME', default='PROJECT_NAME')
ENVIRONMENT = config("PROJECT_ENVIRONMENT_TYPE", default="development")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-wp2v1^#%mv&!m9_d^%@2w@mcjnlgx%_xv-4fgl!las%(vl(yc#'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = config('PROJECT_ALLOWED_HOSTS', cast=Csv(), default='')


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'coex_translator',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'test_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'test_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DJANGO_CACHE_TRANSLATIONS = 'translations'
CACHES = {
    'default': {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
    DJANGO_CACHE_TRANSLATIONS: {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        'LOCATION': '{}:{}:{}'.format(PROJECT_NAME, ENVIRONMENT, DJANGO_CACHE_TRANSLATIONS),
        'TIMEOUT': None,
        'KEY_PREFIX': '{}:{}:{}'.format(PROJECT_NAME, ENVIRONMENT, DJANGO_CACHE_TRANSLATIONS)
    }
}


COEX_TRANSLATOR: "CoexTranslatorSettings" = {
    "API_BASE_URL": config('COEX_TRANSLATOR_API_BASE_URL', default=''),
    "API_TOKEN": config('COEX_TRANSLATOR_API_TOKEN', default=''),
    "UVICORN_RELOAD_FILE_PATH": config('COEX_TRANSLATOR_UVICORN_RELOAD_FILE_PATH', default=''),
    "STARTUP_REFRESH_ENABLED": config('COEX_TRANSLATOR_STARTUP_REFRESH_ENABLED', default=False, cast=bool),
    'FETCH_WITH_FE': False,
    'DISABLE_IN_MANAGEMENT_COMMANDS': False,
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
