import logging

from django.conf import settings
from django.core.cache import caches
from django.utils.translation import get_language, _trans

from coex_translator.publisher import TranslationAMQPPublisher
from coex_translator.singleton import Singleton


logger = logging.getLogger(__name__)


TRANSLATION_UPDATE_MESSAGE = 'update_translations'


class Translator(metaclass=Singleton):

    trans_dict: dict[str, str] = None

    def __init__(self):
        self.trans_dict = {}

    @staticmethod
    def _get_trans_key(message: str, language: str) -> str:
        return f'{language}:{message}'

    def get_trans(self, message: str) -> str:
        language = get_language()
        if not language:
            return message  # Translations are disabled for some reason

        trans_key = self._get_trans_key(message, language)
        trans = self.trans_dict.get(trans_key, None)

        #  Fallback to django cache
        #if not trans:
        #    trans = self._get_trans_from_cache(message=message, language=language)
        #
        #    if trans:
        #        self.trans_dict[trans_key] = trans

        return trans or message

    def _get_trans_from_cache(self, message: str, language: str) -> str:
        cache = caches[settings.DJANGO_TRANSLATIONS_CACHE]

        trans_key = self._get_trans_key(message, language)
        trans = cache.get(trans_key)

        if not trans:
            trans = _trans.gettext(message)

            if trans != message:
                cache.set(trans_key, trans, 3600)

        return trans

    def update_translations(self):
        logger.debug("Cleared translations in memory.")
        self.trans_dict = {}
        #  TODO fetch new translations from storage

    def publish_update_translations(self):
        logger.debug("Sending translations update command.")

        body = TRANSLATION_UPDATE_MESSAGE.encode('utf-8')

        TranslationAMQPPublisher.publish(body)
