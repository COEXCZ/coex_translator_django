import glob
import re
import os

import requests

from django.core.management import BaseCommand, call_command
from django.conf import settings


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg_regex = re.compile(r'^msgid \"(.+)\"$', flags=re.MULTILINE)

    def add_arguments(self, parser):
        parser.add_argument(
            'branch_name',
        )
        parser.add_argument(
            'commit_id',
            nargs='?',
            default=''
        )
        return parser

    def handle(self, *args, **options):
        # TODO: check if COEX_TRANSLATOR_API_BASE_URL is set in settings
        # TODO: check if COEX_TRANSLATOR_API_TOKEN is set in settings

        # TODO: make sure all settings.LOCALE_PATHS exist

        call_command('makemessages', locale=[settings.LANGUAGE_CODE])

        messages = set()
        for locale_path in settings.LOCALE_PATHS:
            po_file_path_pattern = os.path.join(locale_path, settings.LANGUAGE_CODE, 'LC_MESSAGES', '*.po')
            po_files = glob.glob(po_file_path_pattern)
            for file_path in po_files:
                with open(file_path) as file:
                    result = self.msg_regex.findall(file.read())
                messages = messages.union(set(result))
        body = {
            'messages': {msg: None for msg in messages},  # None is the default translation (We don't have it on BE)
            'app_name': settings.PROJECT_NAME,
            'meta': {
                'branch_name': options['branch_name'],
                'commit_id': options.get('commit_id', None)
            }
        }

        requests.post(
            f'{settings.COEX_TRANSLATOR_API_BASE_URL}/message/import/',
            json=body
        )
