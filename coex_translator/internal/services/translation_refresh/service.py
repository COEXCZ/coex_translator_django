import json
import logging

from django.conf import settings
from django.core.cache import caches, BaseCache

from coex_translator.internal import storage, clients
from coex_translator.internal.services.translation_refresh import schemas

logger = logging.getLogger(__name__)


class TranslationRefreshService:
    def refresh_translations(self, languages: list[str] = None) -> list[schemas.Translation]:
        """Refreshes translations for the given languages and saves them to local cache."""
        if languages is None:
            languages = settings.LANGUAGES
        logger.info(f"Refreshing translations for {languages=}.")

        translations: list[schemas.Translation] = []
        for language in languages:
            language_translations = self._get_translations(language)
            translations.extend(language_translations)
        self._save_translations(translations)
        return translations

    def _get_translations(self, language: str) -> list[schemas.Translation]:
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

    def _save_translations(self, translations: list[schemas.Translation]) -> None:
        """Save translations to the cache, so they can start being used."""
        cache: BaseCache = caches[settings.DJANGO_CACHE_TRANSLATIONS]
        cache_dict: dict[str, str] = {self._get_translation_cache_key(tr): tr.translation for tr in translations}
        cache.set_many(cache_dict, timeout=None)

    def _get_storage_translations(self, language: str) -> list[schemas.Translation] | None:
        """
        Download translations from the Object storage.
        :raises: ConnectionError if the download fails.
        """
        translations_file: bytes = storage.S3Storage().download(self._get_storage_path(language))
        translations: list[dict] = json.loads(translations_file.decode())
        return [schemas.Translation(**tr) for tr in translations]

    def _get_translator_translations(self, language: str) -> list[schemas.Translation]:
        """Fetch translations from the Translator service."""
        fetched_translations = clients.TranslatorClient().fetch_translations(language=language)
        translations: list[schemas.Translation] = []
        for fetched_trans in fetched_translations:
            if fetched_trans.language != language:
                # This should not happen, unless the Translator service returns invalid data for some reason.
                logger.error(
                    "Translation language does not match the requested language.",
                    extra={
                        "requested_language": language,
                        "translation_data": fetched_trans.dict(exclude_none=False),
                    }
                )
                continue

            translations.append(
                schemas.Translation(
                    message=fetched_trans.message.key,
                    translation=fetched_trans.translation or "",  # TODO If None. Or should be handled differently?
                    language=fetched_trans.language,
                )
            )
        return translations

    @classmethod
    def _get_storage_path(cls, language: str) -> str:
        """Get the path to the JSON file with translations in the Storage."""
        folder: str = settings.COEX_TRANSLATOR_TRANSLATIONS_STORAGE_FOLDER
        return f"{folder}/{settings.ENVIRONMENT}/{settings.PROJECT_NAME}/{language}/translations.json"

    @classmethod
    def _get_translation_cache_key(cls, translation: schemas.Translation) -> str:
        """Get the cache key for the translation."""
        return f"{translation.language}:{translation.message}"
