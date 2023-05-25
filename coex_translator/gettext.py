import logging

from django.conf import settings
from django.core.cache import caches
from django.utils.functional import lazy
from django.utils import translation
from django.utils.translation import get_language, _trans


logger = logging.getLogger(__name__)


def get_trans(message: str) -> str:
    cache = caches[settings.DJANGO_CACHE_TRANSLATIONS]
    language = get_language()
    cache_key = f'{language}:{message}'

    if not language:
        return message  # Translations are disabled for some reason

    trans = cache.get(cache_key)

    if not trans:
        trans = _trans.gettext(message)
        if trans != message:
            cache.set(cache_key, trans, timeout=60)

    return trans or message


def gettext(message):
    trans = get_trans(message=message)
    return trans or message


ugettext = gettext
ugettext_lazy = gettext_lazy = lazy(gettext, str)

translation.gettext = gettext
translation.gettext_lazy = gettext_lazy
translation.ugettext = gettext
translation.ugettext_lazy = gettext_lazy
