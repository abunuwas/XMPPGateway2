import unittest
from unittest import TestCase

import os
from xml.etree import ElementTree as ET
import logging 

from client_connection import make_bot

from XMPPGateway.sleek.component import Component, make_component
from XMPPGateway.sleek.custom_stanzas import Config
#from XMPPGateway.db_access.sql_sever_interface import DB
#from queueing_systems.sqs import SQS
#from queueing_systems.kinesis import Kinesis


config_dir = os.path.abspath(os.path.join(os.pardir, 'config'))
local_config_file = os.path.join(config_dir, 'config_local.xml')
prod_config_file = os.path.join(config_dir, 'config.xml')


class TestComponent(Component):
    '''
    This class overwrites the stanza handlers of
    the production component to customize their
    behavior for testing purposes. 
    '''
    def __init__(self, *args, **kwargs):
        Component.__init__(self, *args, **kwargs)
        self.test_stanzas = []

    def intamac_api(self, *args, **kwargs):
        self.test_stanzas.append(args)
        Component.intamac_api(self, *args, **kwargs)


class TestQueues(TestCase):
    def test_sqs(self):
        pass

    def test_kinesis(self):
        pass 


class TestStanzas(TestCase):
    
    def setUp(self):
        self.component = make_component(config_path=prod_config_file, cls=TestComponent)
        print(self.component.boundjid)
        self.bot = make_bot('user1')

    def tearDown(self):
        self.component.disconnect()
        self.bot.disconnect()

    def test_intamac_api_stanza(self):
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
        params = {
            'param': '&lt;SoundPackList&gt;&lt;SoundPack&gt;&lt;tag&gt;Aggression&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;BabyCry&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;CarAlarm&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;GlassBreak&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;Gunshot&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;SmokeAlarm&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;/SoundPackList&gt;',
            'url': '/Event/audioanalyse',
            'type': '1'
        }
        self.bot.intamac_api(**params)
        #print('Response is: ', response)
        # The client includes the response into a list. In
        # this case, we expect this list to contain just one
        # element. 
        #self.assertEqual(len(response), 1)
        # Get a string representation of the of response stanza
        # and build an ElementTree object from it:
        #response_string = str(response[0])
        #response_xml = ET.fromstring(response_string)
        # Build a list with each element of the XML:
        #elements = [element for element in response_xml.iter()]
        #print(elements)
        # Get pointers to respectively to the root and the child
        # elements:
        #root, child = elements[0], elements[1]
        # We expect the following parameters in the XML of the
        # response:
        #self.assertEqual(root.tag, 'iq')
        #self.assertEqual(child.tag, 'intamacapi')
        #self.assertEqual(child.url, params['url'])
        #self.assertEqual(child.type, params['type'])
        
        #self.component.intamac_api(api='asdf')
        #self.assertTrue(self.component)
        print('TEST STANZAS ARE: ', self.component.test_stanzas)



class TestComponentConnection(TestCase):

    def setUp(self):
        config_dir = os.path.abspath(os.path.join(os.pardir, 'config'))
        self.local_config_file = os.path.join(config_dir, 'config_local.xml')
        self.prod_config_file = os.path.join(config_dir, 'config.xml')

    def test_comopnent_connects(self):
        config_file = open(self.prod_config_file, 'r+')
        config_data = "\n".join([line for line in config_file])
        config = Config(xml=ET.fromstring(config_data))
        config_file.close()
        xmpp = Component(config)
        xmpp.connect()
        xmpp.process(block=False)
        xmpp.disconnect()


class TestComponentBehavior(TestCase):
    def setUp(self):
        config_dir = os.path.abspath(os.path.join(os.pardir, 'config'))
        local_config_file = os.path.join(config_dir, 'config_local.xml')
        prod_config_file = os.path.join(config_dir, 'config.xml')
        config_file = open(prod_config_file, 'r+')
        config_data = "\n".join([line for line in config_file])
        config = Config(xml=ET.fromstring(config_data))
        config_file.close()
        #logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
        self.component = Component(config)
        self.component.connect()
        self.component.process(block=False)
        self.bot = make_bot('user1')

    def tearDown(self):
        self.bot.disconnect()
        self.component.disconnect()

    def test_presence(self):
        pass

    def test_intamac_api(self):
        response = self.bot.intamac_api()
        # The client includes the response into a list. In
        # this case, we expect this list to contain just one
        # element. 
        self.assertEqual(len(response), 1)
        # Get a string representation of the of response stanza
        # and build an ElementTree object from it:
        response_string = str(response[0])
        response_xml = ET.fromstring(response_string)
        # Expect the tag of the element to be iq:
        self.assertTrue(response_xml.tag, 'iq')


if __name__ == '__main__':
    unittest.main()