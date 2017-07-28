"""
Lambda Queue Consumer Test
"""
import boto3

import unittest
import unittest.mock
import lambda_queue_consumer


class LambdaQueueConsumerTest(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """Setup for testing"""

    def setUp(self):
        self.event

        region_name = 'eu-west-1'
        self.sqs_client = boto3.client('sqs', region_name=region_name)
        self.sts_client = boto3.client('sts', region_name=region_name)
        self.sns_client = boto3.client('sns', region_name=region_name)

    def tearDown(self):
        pass


