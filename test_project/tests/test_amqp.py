from time import sleep
from unittest import mock

import pika
from django.test import TestCase

from coex_translator.app_settings import app_settings
from coex_translator.consumer import ThreadedTranslationAMQPConsumer
from coex_translator.publisher import TranslationAMQPPublisher


class AMQPTestCase(TestCase):

    def setUp(self):
        parameters = pika.URLParameters(app_settings["AMQP"]["BROKER_URL"])
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(
            exchange=app_settings["AMQP"]["EXCHANGE"],
            auto_delete=True,
        )

        self.consumer = ThreadedTranslationAMQPConsumer(daemon=True)
        channel.queue_declare(queue=self.consumer.queue_name, auto_delete=True)
        channel.queue_bind(
            queue=self.consumer.queue_name,
            exchange=app_settings["AMQP"]["EXCHANGE"],
            routing_key=app_settings["AMQP"]["ROUTING_KEY"],
        )

        self.publisher = TranslationAMQPPublisher()

    def tearDown(self):
        self.consumer.stop()

    @mock.patch('coex_translator.consumer.ThreadedTranslationAMQPConsumer.on_message')
    def test_publish_consume(self, on_message_mock):
        from coex_translator.publisher import TranslationAMQPPublisher

        self.publisher.publish_update_translations()

        self.consumer.start()

        sleep(1)

        on_message_mock.assert_called_once_with(TranslationAMQPPublisher.TRANSLATION_UPDATE_MESSAGE.encode('utf-8'))

    @mock.patch('coex_translator.consumer.ThreadedTranslationAMQPConsumer.on_message')
    def test_consumer_retry(self, on_message_mock):
        from coex_translator.publisher import TranslationAMQPPublisher

        self.publisher.publish_update_translations()

        self.consumer.start()

        sleep(1)

        on_message_mock.assert_called_once_with(TranslationAMQPPublisher.TRANSLATION_UPDATE_MESSAGE.encode('utf-8'))

        self.consumer._connection.close()

        sleep(2)

        #  Connection is recovering

        self.publisher.publish_update_translations()

        sleep(1)

        self.assertEqual(on_message_mock.call_count, 2)
