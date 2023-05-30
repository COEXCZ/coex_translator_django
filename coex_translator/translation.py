from django.conf import settings
from django.core.cache import caches
import django.utils.translation
import django.template.base


def gettext(message):
    cache = caches[settings.DJANGO_CACHE_TRANSLATIONS]
    language = django.utils.translation.get_language()
    cache_key = f'{language}:{message}'
    if not language:
        return message  # Translations are disabled for some reason
    trans = cache.get(cache_key)
    if not trans:
        trans = django.utils.translation._trans.gettext(message)
        if trans != message:
            cache.set(cache_key, trans, timeout=60)
    return trans or message


def monkeypatch_translations() -> None:
    from django.utils.functional import lazy

    gettext_lazy = lazy(gettext, str)

    # Override the default gettext functions
    django.utils.translation.gettext = gettext
    django.utils.translation.gettext_lazy = gettext_lazy

    # Added because otherwise in Django 4.1+ {% trans ... %} tags stopped translating
    django.template.base.gettext_lazy = gettext_lazy
