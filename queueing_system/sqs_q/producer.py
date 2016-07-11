import datetime
import time
import sys

import boto3
from botocore.exceptions import ClientError

from queueing_system.sqs_q.core_sqs import get_queue

def push(queue, payload, _from=None):
	response = queue.send_message(MessageBody=payload, 
						MessageAttributes={
											'TimeStamp': {
														'StringValue': str(datetime.datetime.now()),
														'DataType': 'String'
											}
						})
	return response

intamacapi = {
	'MessageBody': '&lt;SoundPackList&gt;&lt;SoundPack&gt;&lt;tag&gt;Aggression&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;BabyCry&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;CarAlarm&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;GlassBreak&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;Gunshot&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;SmokeAlarm&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;/SoundPackList&gt;',
	'MessageAttributes': {
					'TimeStamp': {
								'StringValue': str(datetime.datetime.now()),
								'DataType': 'String'
					},
					'namespace': {
								'StringValue': 'intamacapi',
								'DataType': 'String'
					},
					'url': {
								'StringValue': '/Event/audioanalyse',
								'DataType': 'String'
					},
					'type': {
								'StringValue': '1',
								'DataType': 'String'
					},
					'to': {
								'StringValue': 'user1@use-xmpp-01/test',
								'DataType': 'String'
					}
				}
}
intamacstream = {
	'MessageBody': '000000000000000000000000000000000000000000000000000000000000',
	'MessageAttributes': {
					'TimeStamp': {
								'StringValue': str(datetime.datetime.now()),
								'DataType': 'String'
					},
					'namespace': {
								'StringValue': 'intamacstream',
								'DataType': 'String'
					},
					'ip': {
								'StringValue': '192.168.1.100',
								'DataType': 'String'
					},
					'port': {
								'StringValue': '50000',
								'DataType': 'String'
					},
					'timeout': {
								'StringValue': '10',
								'DataType': 'String'
					},
					'quality': {
								'StringValue': 'sub',
								'DataType': 'String'
					},
					'type': {
								'StringValue': 'start',
								'DataType': 'String'
					},
					'to': {
								'StringValue': 'user1@use-xmpp-01/test',
								'DataType': 'String'
					}
				}
}
intamacfirmwareupgrade = {
	'MessageBody': 'default',
	'MessageAttributes': {
					'TimeStamp': {
								'StringValue': str(datetime.datetime.now()),
								'DataType': 'String'
					},
					'namespace': {
								'StringValue': 'intamacfirmwareupgrade',
								'DataType': 'String'
					},
					'location': {
								'StringValue': 'https://stg.upgrade.swann.intamac.com/swa_firmware_v505_151020.dav',
								'DataType': 'String'
					},
					'to': {
								'StringValue': 'user1@use-xmpp-01/test',
								'DataType': 'String'
					}
				}
}
intamacsetting = {
	'MessageBody': 'default',
	'MessageAttributes': {
					'TimeStamp': {
								'StringValue': str(datetime.datetime.now()),
								'DataType': 'String'
					},
					'namespace': {
								'StringValue': 'intamacsetting',
								'DataType': 'String'
					},
					'xmppip': {
								'StringValue': '192.168.1.100',
								'DataType': 'String'
					},
					'buddy': {
								'StringValue': 'mzclientxmppapp@xmpp.intamac.com/xmppadmin',
								'DataType': 'String'
					},
					'to': {
								'StringValue': 'user1@use-xmpp-01/test',
								'DataType': 'String'
					}
				}
} 

stanzas = [intamacapi, intamacsetting, intamacstream, intamacfirmwareupgrade]

def test(queue, device):
	import random
	e = 0
	while e < 10:
		index = random.randint(0, len(stanzas)-1)
		print(index)
		stanza = stanzas[index]
		print(stanza['MessageAttributes']['namespace'])
		response = queue.send_message(**stanza)
		print(response)
		time.sleep(.5)
		e += 1

if __name__ == '__main__':
	import threading
	queue = get_queue(queue_test)
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
