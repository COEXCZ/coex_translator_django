import typing

from coex_translator.singleton import Singleton

LangCodeStr = str  # 2-letter language code



class TranslationService(Singleton):
    """Singleton service for retrieving/setting translations."""
    _TRANSLATIONS: typing.ClassVar[dict[str, str]] = {}  # {cache_key: translation}

    @classmethod
    def set(cls, message_key: str, translation: str, language: LangCodeStr) -> None:
        """Save translation for given language."""
        cache_key = cls.get_cache_key(message_key, language)
        cls._TRANSLATIONS[cache_key] = translation

    @classmethod
    def set_many(cls, translations: dict[str, str], language: LangCodeStr) -> None:
        """
        Save translations for given language.
        @param translations: {message_key: translation}
        @param language: 2-letter language code
        """
        for message_key, translation in translations.items():
            cls.set(message_key, translation, language)

    @classmethod
    def get(cls, message_key: str, language: LangCodeStr) -> str:
        """Get the translation for the given language and message key."""
        # TODO discuss - if settings.LANGUAGE_CODE has translation -> return that instead of the message_key default??
        cache_key = cls.get_cache_key(message_key, language)
        return cls._TRANSLATIONS.get(cache_key, message_key)

    @classmethod
    def clear(cls) -> None:
        """Clears the translations."""
        cls._TRANSLATIONS.clear()


    @classmethod
    def get_cache_key(cls, message_key: str, language: LangCodeStr) -> str:
        """Get the cache key for the given language and message key."""
        return f"{language}:{message_key}"

