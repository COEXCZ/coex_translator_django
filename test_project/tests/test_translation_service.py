from django.core.cache import caches
from django.conf import settings
from django.test import TestCase
from coex_translator.service import TranslationService

cache = caches[settings.DJANGO_CACHE_TRANSLATIONS]


class TranslationServiceTestCase(TestCase):
    def setUp(self):
        self.service = TranslationService

    def test_is_singleton(self):
        self.assertEqual(id(self.service), id(TranslationService))

    def test_set(self):
        key, translation, lang = "message-key", "Translated text", "en"
        self.service.set(key, translation, lang)
        self.assertEqual(self.service.get(key, lang), translation)

    def test_set_the_same_key_with_different_language(self):
        key = "message-key"
        translation, lang = "Translated text", "en"
        translation2, lang2 = f"{translation} Other language", "fr"

        self.service.set(key, translation, lang)
        self.service.set(key, translation2, lang2)

        self.assertEqual(self.service.get(key, lang), translation)
        self.assertEqual(self.service.get(key, lang2), translation2)

    def test_set_replaces_translations_for_given_language_only(self):
        key = "message-key"
        translation, lang = "Translated text", "en"
        translation_new = f"{translation} Other language"
        translation_other_lang, lang_other = f"{translation} Other language", "fr"

        self.service.set(key, translation, lang)
        self.service.set(key, translation_other_lang, lang_other)
        self.service.set(key, translation_new, lang)

        self.assertEqual(self.service.get(key, lang), translation_new)
        self.assertEqual(self.service.get(key, lang_other), translation_other_lang)

    def test_set_many(self):
        translations = {
            "message-key-1": "Translated text 1",
            "message-key-2": "Translated text 2",
        }
        lang = "en"
        self.service.set_many(translations, lang)
        for key, translation in translations.items():
            self.assertEqual(self.service.get(key, lang), translation)
