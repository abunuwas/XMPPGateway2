import multiprocessing as mp
import logging
import atexit

from client_connection import make_bot
from component_connection import make_component
from component_connection import config_dir
from XMPPGateway.sleek.component import Component

import threading as mt

def make_test(clients):
    jobs = []

    component = mt.Thread(target=make_component, args=(config_dir, Component))

    jobs.append(component)

    for i in range(clients):
        client = mt.Thread(target=make_bot, args=('user{}'.format(i), 'localhost', 'mypassword', config_dir))
        jobs.append(client)

    for j in jobs:
        j.start()

if __name__ == '__main__':
    #xmpp = None

    #def exit_handler():
    #    xmpp.disconnect()

    #atexit.register(exit_handler)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('nose').setLevel(logging.WARNING)
    
    make_test(100)