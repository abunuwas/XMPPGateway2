import datetime

import boto3
from botocore.exceptions import ClientError

sqs = boto3.resource('sqs')

queue_name = 'test'

outcomes = {}

def get_queue(queue_name):
    try:
        queue = sqs.get_queue_by_name(QueueName=queue_name)
        return queue
    except ClientError:
        print('The requested queue does not exist.')

def poll(queue, p_id=None):
    while True:
        #print('new loop')
        for message in queue.receive_messages(MessageAttributeNames=['*']):
            #print(message.body)
            data = {}
            param = message.body
            if data != 'default':
                data['param'] = param
            attributes = message.message_attributes
            for attr, value in attributes.items():
                data[attr] = value['StringValue']
            #print(data)
            yield data
            #namespace = message.message_attributes.get('namespace').get('StringValue')
            #print(namespace)
            #print(message.message_attributes)
            #yield data
            #if device not in outcomes.keys():
            #   outcomes[device] = [message.body]
            #else:
            #   outcomes[device].append(message.body)
            message.delete()

if __name__ == '__main__':
    queue = get_queue(queue_name)
    poll(queue)
    '''
    import multiprocessing as mp
    queue = get_queue(queue_name)
    #message = poll(queue)
    jobs = []
    for i in range(1):
        process = mp.Process(target=poll, args=(queue, i))
        jobs.append(process)
    for j in jobs:
        j.start()
    '''
    '''
    try:
        poll(queue)
    except KeyboardInterrupt:
        for key, data in outcomes.items():
            print('\n\n')
            print(key)
            print('-'*10)
            for value in data:
                print(value)
    '''

