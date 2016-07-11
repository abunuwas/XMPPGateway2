import datetime
import time

import boto3
from botocore.exceptions import ClientError

from queueing_system.sqs_q.core_sqs import get_queue

outcomes = {}

def poll(queue, p_id=None, sleep=None):
    while True:
        #print('new loop')
        a = None
        for message in queue.receive_messages(MessageAttributeNames=['*']):
            a = message
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
        if a is None:
            pass
        if sleep:
            time.sleep(sleep)

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO,
                        format='%(levelname)-8s %(message)s')
    queue = get_queue(queue_name)
    poll(queue, sleep=2)
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

