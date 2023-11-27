from django.core.management import BaseCommand, CommandError

from coex_translator.internal import clients


class Command(BaseCommand):
    help = ('Publish translations in COex Translator to the storage and notify the containers to refresh them.'
            ' Usable after deploy')

    def add_arguments(self, parser):
        parser.add_argument(
            'environment',
            help="Environment to publish translations to. Currently must be one of: 'testing', 'production",
        )
        return parser

    def handle(self, *args, **options):

        environment = args[0]

        if environment not in ['testing', 'production']:  # Hardcoded, modify with COex translator
            raise CommandError('Environment must be one of: "testing", "production"')

        self.stdout.write(f"Calling COex Translator API to publish translations for environment {environment}.")

        publish_results = clients.TranslatorClient().publish_translations(environment)

        self.stdout.write(f"Done. Publish results are: {publish_results.items}.")
