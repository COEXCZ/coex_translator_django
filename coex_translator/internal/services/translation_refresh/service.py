import json
import logging

from django.conf import settings
from django.core.cache import caches, BaseCache

from coex_translator.app_settings import app_settings
from coex_translator.internal import storage, clients, constants

logger = logging.getLogger(__name__)
TranslationsType = dict[str, str]  # message_key: translation
LangCodeStr = str  # 2-letter language code


class TranslationRefreshService:
    def refresh_translations(self, languages: list[LangCodeStr] = None) -> dict[LangCodeStr, TranslationsType]:
        """Refreshes translations for the given languages and saves them to local cache."""
        if languages is None:
            languages = [code for code, name in settings.LANGUAGES]
        logger.info(f"Refreshing translations for {languages=}.")

        translations: dict[LangCodeStr, TranslationsType] = {}
        for language in languages:
            language_translations = self._get_translations(language)
            translations[language] = language_translations
            self._save_translations(language_translations, language)
        return translations

    def _get_translations(self, language: LangCodeStr) -> TranslationsType:
        # Try to load the translations from Object storage.
        try:
            return self._get_storage_translations(language)
        except storage.S3Storage.ConnectionError as e:
            logger.error(
                f"Unable to download translations for language `{language} from the storage. "
                f"Fetching from Translator service.",
                extra={
                    'error': str(e),
                }
            )
        except storage.S3Storage.ObjectNotFoundError as e:
            logger.error(
                f"Translations for language `{language}` not found in the storage. Fetching from Translator service.",
                extra={
                    'path': e.path,
                }
            )
        # As a backup, try to fetch them from the Translator service.
        return self._get_translator_translations(language)

    def _save_translations(self, translations: TranslationsType, language: LangCodeStr) -> None:
        """Save translations to the cache, so they can start being used."""
        cache: BaseCache = caches[settings.DJANGO_CACHE_TRANSLATIONS]
        cache_dict: dict[str, str] = {
            f"{language}:{message_key}": translation
            for message_key, translation in translations.items()
        }
        cache.set_many(cache_dict, timeout=None)

    def _get_storage_translations(self, language: LangCodeStr) -> TranslationsType:
        """
        Download translations from the Object storage.
        :raises: ObjectNotFoundError if the translation file is not found.
        :raises: ConnectionError if the download fails.
        """
        translations_file: bytes = storage.S3Storage().download(self._get_storage_path(language))
        translations: TranslationsType = json.loads(translations_file.decode())
        return {msg_key: trans for msg_key, trans in translations.items() if trans is not None}

    def _get_translator_translations(self, language: LangCodeStr) -> TranslationsType:
        """Fetch translations from the Translator service."""
        fetched_translations = clients.TranslatorClient().fetch_translations(language=language)
        return {t.message.key: t.translation for t in fetched_translations if t.translation is not None}

    @classmethod
    def _get_storage_path(cls, language: LangCodeStr) -> str:
        """Get the path to the JSON file with translations in the Storage."""
        folder: str = app_settings['STORAGE']['FOLDER']
        return f"{folder}/{settings.ENVIRONMENT}/{constants.APP_NAME}/{language}/translations.json"
