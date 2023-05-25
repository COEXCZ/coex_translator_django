from django.core.management import BaseCommand

from coex_translator.consumer import ThreadedTranslationAMQPConsumer


class Command(BaseCommand):
    help = 'Starts the translation AMQP consumer'

    def handle(self, *args, **options):
        translation_consumer = ThreadedTranslationAMQPConsumer()
        translation_consumer.start()
        translation_consumer.join()