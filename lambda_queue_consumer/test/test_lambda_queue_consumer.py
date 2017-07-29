"""
Lambda Queue Consumer Test
"""

from pprint import pprint
import unittest
from unittest.mock import MagicMock, call
import lambda_queue_consumer.lambda_queue_consumer


class LambdaQueueConsumerTest(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """Setup for testing"""

    def setUp(self):
        self.event = {
            'queue': 'nest-test-queue',
            'dead-letter-queue': 'nest-test-dead-letter-queue'
        }
        self.consumer = lambda_queue_consumer.lambda_queue_consumer.LambdaQueueConsumer()
        self.consumer.sts_client.get_caller_identity = MagicMock(return_value={
            'Account': 'test-account'
        })

        self.consumer.sqs_client.create_queue = MagicMock(return_value={
            'QueueUrl': 'aws:test-queue-url'
        })
        self.consumer.sqs_client.get_queue_url = MagicMock(return_value={
            'QueueUrl': 'nest-test-queue-url'
        })
        self.consumer.sqs_client.send_message = MagicMock(return_value={
            'MD5OfMessageBody': 'test-md5',
            'MD5OfMessageAttributes': 'test-md5',
            'MessageId': 'test-message-id',
            'SequenceNumber': 'test-sequence-number'
        })
        self.consumer.sqs_client.receive_message = MagicMock(return_value={
            'Messages': [
                {
                    'MessageId': 'test-message-id-1',
                    'ReceiptHandle': 'test-receipt-handle-1',
                    'MD5OfBody': 'test-md5-1',
                    'Body': 'test-body-1',
                    'Attributes': {
                        'test-attribute': 'test-attribute-value'
                    }
                },
                {
                    'MessageId': 'test-message-id-2',
                    'ReceiptHandle': 'test-receipt-handle-2',
                    'MD5OfBody': 'test-md5-2',
                    'Body': 'test-body-2',
                    'Attributes': {
                        'test-attribute': 'test-attribute-value'
                    }
                }
            ]
        })
        self.consumer.sqs_client.delete_message = MagicMock(return_value=None)

        self.consumer.sns_client.create_topic = MagicMock(return_value={
            'TopicArn': 'arn:aws:sns:eu-west-1:458315597956:nest-test-topic'
        })
        self.consumer.sns_client.publish = MagicMock(return_value={
            'MessageId': 'test-message-id'
        })
        self.consumer.sns_client.list_subscriptions_by_topic = MagicMock(return_value={
            'Subscriptions': [
                {
                    'SubscriptionArn':
                        'arn:aws:sns:eu-west-1:458315597956:nest-test-notifier:0a314486-a412-40c3-ae62-8c1b00btest1',
                    'Owner': 'test-owner',
                    'Protocol': 'email',
                    'Endpoint': 'soppela.jyri@gmail.com',
                    'TopicArn': 'arn:aws:sns:eu-west-1:458315597956:nest-test-notifier'
                },
                {
                    'SubscriptionArn':
                        'arn:aws:sns:eu-west-1:458315597956:nest-test-notifier:0a314486-a412-40c3-ae62-8c1b00btest2',
                    'Owner': 'test-owner',
                    'Protocol': 'email',
                    'Endpoint': 'soppela.jyri@gmail.com',
                    'TopicArn': 'arn:aws:sns:eu-west-1:458315597956:nest-test-notifier'
                },
            ]
        })

    def tearDown(self):
        pass

    def test_message_distribution(self):
        self.consumer.distribute_data(self.event)

        # Test account operations
        self.assertTrue(self.consumer.sts_client.get_caller_identity.called)

        # Test outgoing queue creation
        self.assertTrue(self.consumer.sqs_client.create_queue.called)
        self.assertEqual(self.consumer.sqs_client.create_queue.call_count,
                         len(self.consumer.sns_client.list_subscriptions_by_topic.return_value['Subscriptions']) *
                         len(self.consumer.sqs_client.receive_message.return_value['Messages']))
        create_queue_calls = [
            call(QueueName='nest-test-queue-0a314486-a412-40c3-ae62-8c1b00btest1'),
            call(QueueName='nest-test-queue-0a314486-a412-40c3-ae62-8c1b00btest2')
        ]
        self.consumer.sqs_client.create_queue.assert_has_calls(create_queue_calls, any_order=True)

        # Test queue URL fetching
        self.assertTrue(self.consumer.sqs_client.get_queue_url.called)

        # Test queue reading
        self.assertTrue(self.consumer.sqs_client.receive_message.called)

        # Test acknowledging receiving messages from queue
        self.assertTrue(self.consumer.sqs_client.delete_message.called)

        # Test message sending
        self.assertTrue(self.consumer.sqs_client.send_message.called)

        # Test notification operations
        self.assertTrue(self.consumer.sns_client.create_topic.called)
        self.assertTrue(self.consumer.sns_client.list_subscriptions_by_topic.called)
        self.assertTrue(self.consumer.sns_client.publish.called)
