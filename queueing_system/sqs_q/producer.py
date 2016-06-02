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

def push(queue, payload, _from):
	response = queue.send_message(MessageBody=payload, 
						MessageAttributes={
											'from': _from,
											'timestamp': datetime.datetime.now()
											}
						)
	return response

if __name__ == '__main__':
	queue = get_queue(queue_name)
	response = push(queue, 'This is a message', 'Camera_1')