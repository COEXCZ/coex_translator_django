import glob
import json
import re
import os

from django.core.management import BaseCommand, call_command, CommandError
from django.conf import settings


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.msg_regex = re.compile(r'^msgid \"(.+)\"$', flags=re.MULTILINE)

    def add_arguments(self, parser):
        parser.add_argument(
            '--file_path',
            help="If provided, exports json file with the translations to given path. Should be a full path.",
            nargs='?',
            default='',
        )
        return parser

    def handle(self, *args, **options):
        # TODO: check if COEX_TRANSLATOR_API_BASE_URL is set in settings
        # TODO: check if COEX_TRANSLATOR_API_TOKEN is set in settings
        # TODO: make sure all settings.LOCALE_PATHS exist

        export_file_path: str = options.pop('file_path', '')
        if export_file_path and export_file_path.split('.')[-1] != 'json':
            raise CommandError('Export file must be a json file. Did you forget to specify the file name or extension?')

        self.stdout.write("Running Django makemessages command...")
        call_command('makemessages', locale=[settings.LANGUAGE_CODE])
        if not export_file_path:
            return

        self.stdout.write(f"Exporting messages into {export_file_path}...")
        messages: set[str] = set()  # message ids
        for locale_path in settings.LOCALE_PATHS:
            po_file_path_pattern = os.path.join(locale_path, settings.LANGUAGE_CODE, 'LC_MESSAGES', '*.po')
            po_files = glob.glob(po_file_path_pattern)
            for file_path in po_files:
                with open(file_path) as file:
                    result = self.msg_regex.findall(file.read())
                messages = messages.union(set(result))

        with open(export_file_path, "w") as f:
            f.write(json.dumps({message: None for message in messages}))
        self.stdout.write(f"Done. {len(messages)} exported to {export_file_path} file.")
