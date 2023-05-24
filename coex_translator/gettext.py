import logging

from django.utils.functional import lazy
from django.utils import translation

from coex_translator.translator import Translator

logger = logging.getLogger(__name__)


def gettext(message):
    translator = Translator()
    trans = translator.get_trans(message=message)
    return trans or message


ugettext = gettext
ugettext_lazy = gettext_lazy = lazy(gettext, str)

translation.gettext = gettext
translation.gettext_lazy = gettext_lazy
translation.ugettext = gettext
translation.ugettext_lazy = gettext_lazy
