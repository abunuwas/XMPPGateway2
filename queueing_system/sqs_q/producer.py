import datetime
import time

import boto3
from botocore.exceptions import ClientError

sqs = boto3.resource('sqs')

queue_name = 'test'

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

def test(queue, device):
	e = 0
	while e < 30:
		response = queue.send_message(MessageBody=device+'_'+str(e),
							MessageAttributes={'TimeStamp': {
															'StringValue': str(datetime.datetime.now()),
															'DataType': 'String'
															}
							})
		print(response)
		time.sleep(.3)
		e += 1

if __name__ == '__main__':
	import threading
	queue = get_queue(queue_name)
	#test(queue)
	#response = push(queue, 'This is a message', 'Camera_1')
	threads = []
	devices = ['camera', 'DVR', 'motionDetector', 'car', 'computer', 'fireAlarm']
	for i in range(1):
		thread = threading.Thread(target=test, args=(queue, devices[i]))
		threads.append(thread)
	e=0
	for thread in threads:
		thread.start()
		print('started thread n. ', e)
		e+=1