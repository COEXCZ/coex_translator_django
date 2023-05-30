import json
import logging

from django.conf import settings
from django.core.cache import caches, BaseCache

from coex_translator._internal import storage, clients
from coex_translator._internal.services.translation_refresh import schemas

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

    def _save_translations(self, translations: list[schemas.Translation]) -> None:
        cache: BaseCache = caches[settings.DJANGO_CACHE_TRANSLATIONS]
        cache_dict: dict[str, str] = {self._get_translation_cache_key(tr): tr.translation for tr in translations}
        cache.set_many(cache_dict, timeout=None)

    def _get_translations(self, language: str) -> list[schemas.Translation]:
        # First, try to load the translations from Object storage.
        translations = self._get_storage_translations(language)
        if translations:
            return translations
        # Second, as a backup, try to fetch them from the Translator service.
        logger.warning(f"Translations for `{language}` not found in the Storage. Fetching from Translator service.")
        return self._get_translator_translations(language)

    def _get_storage_translations(self, language: str) -> list[schemas.Translation] | None:
        translations_file: bytes = storage.S3Storage().download(self._get_storage_path(language))
        if not translations_file:  # TODO test what happens if does not exist or is empty
            return
        translations: list[dict] = json.loads(str(translations_file))
        return [schemas.Translation(**tr) for tr in translations]

    def _get_translator_translations(self, language: str) -> list[schemas.Translation]:
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
