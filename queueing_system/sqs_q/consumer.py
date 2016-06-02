import datetime

import boto3
from botocore.exceptions import ClientError

sqs = boto3.resource('sqs')

queue_name = 'test-queue'

def get_queue(queue_name):
	try:
		queue = sqs.get_queue_by_name(QueueName=queue_name)
		return queue
	except ClientError:
		print('The requested queue does not exist.')

def poll(queue):
	for messages in queue.receive_messages():
		return message

if __name__ == '__main__':
	queue = get_queue(queue_name)
	message = poll(queue)