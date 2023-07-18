import logging

import django.template
import django.utils

from django.utils import translation

from coex_translator.service import TranslationService

logger = logging.getLogger(__name__)


def get_trans(message: str) -> str:
    language = django.utils.translation.get_language()
    translation_service = TranslationService()
    if not language:
        return message  # Translations are disabled for some reason

    trans = translation_service.get(message, language)

    if not trans:
        trans = django.utils.translation._trans.gettext(message)
        if trans != message:
            translation_service.set(message, translation=trans, language=language)

    return trans or message


def gettext(message):
    trans = get_trans(message=message)
    return trans or message


def monkeypatch_translations() -> None:
    from django.utils.functional import lazy

    gettext_lazy = lazy(gettext, str)

    # Override the default gettext functions
    django.utils.translation.gettext = gettext
    django.utils.translation.gettext_lazy = gettext_lazy

    # Added because otherwise in Django 4.1+ {% trans ... %} tags stopped translating
    django.template.base.gettext_lazy = gettext_lazy
