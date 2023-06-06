import signal
import logging

from django.core.management import BaseCommand

from coex_translator.consumer import ThreadedTranslationAMQPConsumer


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Starts the translation AMQP consumer'

    def handle(self, *args, **options):
        translation_consumer = ThreadedTranslationAMQPConsumer()

        def receive_signal(signum, stack):
            logger.info('Received SIGTERM: Warm shutdown.')
            translation_consumer.stop()

        signal.signal(signal.SIGTERM, receive_signal)
        signal.signal(signal.SIGINT, receive_signal)

        translation_consumer.start()
