from time import sleep
from unittest import mock

from django.test import TestCase


class AMQPTestCase(TestCase):

    @mock.patch('coex_translator.consumer.ThreadedTranslationAMQPConsumer.on_message')
    def test_publish_consume(self, on_message_mock):
        from coex_translator.publisher import TranslationAMQPPublisher
        from coex_translator.consumer import ThreadedTranslationAMQPConsumer

        consumer = ThreadedTranslationAMQPConsumer()

        publisher = TranslationAMQPPublisher()
        publisher.publish_update_translations()

        consumer.start()
        consumer.join(timeout=1)

        on_message_mock.assert_called_once_with(TranslationAMQPPublisher.TRANSLATION_UPDATE_MESSAGE.encode('utf-8'))

        consumer.stop()
