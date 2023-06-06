from unittest import mock

import pika
from django.conf import settings
from django.test import TestCase

from coex_translator.consumer import ThreadedTranslationAMQPConsumer
from coex_translator.publisher import TranslationAMQPPublisher


class AMQPTestCase(TestCase):

    def setUp(self):
        parameters = pika.URLParameters(settings.COEX_TRANSLATOR_AMQP_BROKER_URL)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=settings.COEX_TRANSLATOR_AMQP_EXCHANGE,
            auto_delete=True,
        )

        self.consumer = ThreadedTranslationAMQPConsumer()
        channel.queue_declare(queue=self.consumer.queue_name, auto_delete=True)
        channel.queue_bind(
            queue=self.consumer.queue_name,
            exchange=settings.COEX_TRANSLATOR_AMQP_EXCHANGE,
            routing_key=settings.COEX_TRANSLATOR_AMQP_ROUTING_KEY
        )

        self.publisher = TranslationAMQPPublisher()

    def tearDown(self):
        self.consumer.stop()

    @mock.patch('coex_translator.consumer.ThreadedTranslationAMQPConsumer.on_message')
    def test_publish_consume(self, on_message_mock):
        from coex_translator.publisher import TranslationAMQPPublisher

        self.publisher.publish_update_translations()

        self.consumer.start()
        self.consumer.join(timeout=1)

        on_message_mock.assert_called_once_with(TranslationAMQPPublisher.TRANSLATION_UPDATE_MESSAGE.encode('utf-8'))
