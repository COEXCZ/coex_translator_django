import typing

from coex_translator.singleton import Singleton

LangCodeStr = str  # 2-letter language code



class TranslationService(metaclass=Singleton):
    """Singleton service for retrieving/setting translations."""
    _TRANSLATIONS: typing.ClassVar[dict[str, str]] = {}  # {cache_key: translation}

    def set(self, message_key: str, translation: str, language: LangCodeStr) -> None:
        """Save translation for given language."""
        cache_key = self.get_cache_key(message_key, language)
        self._TRANSLATIONS[cache_key] = translation

    def set_many(self, translations: dict[str, str], language: LangCodeStr) -> None:
        """
        Save translations for given language.
        @param translations: {message_key: translation}
        @param language: 2-letter language code
        """
        for message_key, translation in translations.items():
            self.set(message_key, translation, language)

    def get(self, message_key: str, language: LangCodeStr) -> str:
        """Get the translation for the given language and message key."""
        # TODO discuss - if settings.LANGUAGE_CODE has translation -> return that instead of the message_key default??
        cache_key = self.get_cache_key(message_key, language)
        return self._TRANSLATIONS.get(cache_key, message_key)

    def clear(self) -> None:
        """Clears the translations."""
        self._TRANSLATIONS.clear()


    @classmethod
    def get_cache_key(cls, message_key: str, language: LangCodeStr) -> str:
        """Get the cache key for the given language and message key."""
        return f"{language}:{message_key}"

