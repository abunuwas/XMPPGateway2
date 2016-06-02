#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Intamac Systems Ltd. All Rights Reserved. 
# 
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
:module: sleek.custom_stanzas.
:author: Jose Haro (jharoperalta@intamac.com).
:synopsis: Custom stanza implementations. 
:platforms: Linux and Unix.
:python-version: Python 3. 

This module defines a class to implement the Component kind
of connection to the XMPP server. 

.. WARNING:: In its current state, the module defines only a basic
             implementation of the component. Further additions are 
             needed in the following direction:
             - Ensures that the component actually deals correctly
               with all sort of stanzas coming to it.
             - Include `try`-`except` clauses to catch all sort of
               possible exceptions that might be raised in different
               situations.
             - Enable logging functionality.
             - Enable proper management capabilities for the flow of
               communication with the DVRs. 
             - Separate the testing functionality into a test-oriented
               implementation of the component. 
             - Ensure that the available plugins from the SleekXMPP
               library are used and leveraged to the highest extent
               possible. 
             - Ensure also that the currently registered plugins are
               used properly and to the highest extent possible. 
             - Include functionality to manage the component roster.
             - Ensure that the path chosen to deal with custom stanzas
               (both plugin registartion and custom class implementation
               of the method listeners to process received stanzas) is
               the most adequate to facilitate the highest possible 
               separation of concerns in the further development of 
               this codebase. For example, if state is not needed to
               deal with the stanzas, their custom processing methods 
               could be implemented in the code of the actual stanzas,
               thereby keeping the component code short, clean, and 
               isolated from issues that might not be its concern here. 
             - Ensure that by all means presence stanzas are handled in
               the most efficient and expected way. 
             - Include parameters to allow the initialization of the 
               component in threaded mode or not. 

Classes
-------
.. ConfigComponent
"""

import sys
import logging
import time
from optparse import OptionParser
import threading 

from queueing_system.queueing import queue_push
from db_access.sql_server_interface import get_connection, get_data

import sleekxmpp
from sleekxmpp import roster
from sleekxmpp.componentxmpp import ComponentXMPP
from sleekxmpp.stanza.roster import Roster
from sleekxmpp.xmlstream import ElementBase
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin, register_stanza_plugin
from sleekxmpp.jid import JID
from sleekxmpp.stanza.iq import Iq
from sleekxmpp.stanza.presence import Presence
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher.xpath import MatchXPath
from sleekxmpp.xmlstream.matcher import StanzaPath

from sleek.custom_stanzas import (DeviceInfo, 
                                IntamacStream, 
                                IntamacFirmwareUpgrade, 
                                IntamacAPI, 
                                IntamacEvent, 
                                Config
                                )

import atexit 


register_stanza_plugin(Config, Roster)

# The three lines of code below serve testing purposes. They should
# not be present in production code. 

threaded = True

messages = []

connections = ['c42f90b752dd@use-xmpp-01/camera', 
                'c42f90b752dd@use-xmpp-01', 
                'user0@use-xmpp-01']


class ConfigComponent(ComponentXMPP):

    """
    A simple SleekXMPP component that uses an external XML
    file to store its configuration data. To make testing
    that the component works, it will also echo messages sent
    to it.
    """

    def __init__(self, config):
        """
        Create a ConfigComponent.

        Arguments:
            config      -- The XML contents of the config file.
            config_file -- The XML config file object itself.
        """
        ComponentXMPP.__init__(self, config['jid'],
                                     config['secret'],
                                     config['server'],
                                     config['port'], use_jc_ns=False)

        custom_stanzas = {
            DeviceInfo: self.intamac_device_info,
            IntamacStream: self.intamac_stream,
            IntamacFirmwareUpgrade: self.intamac_firmware_upgrade,
            IntamacAPI: self.intamac_api,
            IntamacEvent: self.intamac_event
        }

        for custom_stanza, handler in custom_stanzas.items():
            register_stanza_plugin(Iq, custom_stanza)
            self.register_handler(
                Callback(custom_stanza.plugin_attrib,
                    StanzaPath('iq@type=set/{}'.format(custom_stanza.plugin_attrib)),
                    handler)
                )

        # The lines of code below configure support for the xep-0203
        # to be able to receive and process specific presence delayed
        # stanzas. I don't think this is the right way to do this,
        # as just registering the plugin should be enough to accomplish
        # the expected behavior. Something to look at later on. 
        from sleekxmpp.plugins.xep_0203 import Delay

        register_stanza_plugin(Presence, Delay)

        self.register_handler(
            Callback(Delay.name,
                StanzaPath('presence/{}'.format(Delay.plugin_attrib)),
                self.delay)
            )

        # The following piece of code shows how a normal registration
        # process for a single stanza plugin takes place: 
        '''
        self.register_handler(
            Callback('iq_api',
                StanzaPath('iq@type=set/iq_intamacapi'),
                self.intamac_device_info))
        
        '''

        # The following lines of code take care of registering 
        # specific listener methods for every kind of stanza that
        # we want to process. The code will be cleaned once a final
        # decision regarding the best way to deal with this is 
        # rechaed. 

        self.add_event_handler("session_start", self.start, threaded=True)
        #self.add_event_handler('presence', self.presence, threaded=threaded)
        #self.add_event_handler('iq_intamacdeviceinfo', self.intamac_device_info, threaded=True)
        self.add_event_handler('presence_subscribe', self.subscribe, threaded=threaded)
        self.add_event_handler('presence_subscribed', self.subscribed, threaded=threaded)  
        self.add_event_handler('delay', self.delay, threaded=threaded)  
        #self.add_event_handler('presence_probe', self.probe, threaded=threaded)
        #self.add_event_handler("message", self.message, threaded=threaded)
        #self.add_event_handler('iq', self.iq, threaded=True)

        if self.check_is_first(self):
        	self.check_status_devices()

    # The usefulness of this class method is not yet clear, but might prove useful
    # later on. 
    @classmethod
    def variables(cls):
        return cls.__dict__

    def start(self, event):
        # Using the method send_presence() without arguments should just work. The problem
        # is that ejabberd then takes the presence from the component (muc.localhost) and 
        # sends it to itself (muc.localhost), resulting in an error. The error seems to 
        # arise from the fact that a presence is being sent from a JID to the same JID.
        # The solution that I can think of for the moment is to explicitly define 
        # a specific destination and a different sender JID. 
        self.send_presence(pto=connections[1], pfrom=self.boundjid.bare, ptype='probe')
        self.poll_queue()

    def check_status_devices(self):
    	devices = self.obtain_list_devices()

    def obtain_list_devices(self):
    	pass

    def check_is_first(self):
    	return True

    def presence(self, presence):
        print(presence)
        '''
        print('TYPE: ', presence['type'])
        _from = JID(presence['from']).bare
        print(_from)
        if self.boundjid.bare not in _from:
            self.send_presence(pto=_from, pfrom=self.boundjid.bare + '/test')
        '''

    def subscribe(self, presence):
        print(presence)
        print('This should be subscribe: ', presence['type'])
        self.send_presence(pto=presence['from'],
                          pfrom=self.boundjid.bare + '/test',
                          ptype='available')

    def subscribed(self, presence):
        print(presence)
        print('This should be subscribed: ', presence['type'])
        self.send_presence(pto=presence['from'], pfrom=self.boundjid.bare, ptype='subscribed')        
        

    def message(self, msg):
        print(msg)
        messages.append(msg)
        print('MESSAGES RECEIVED: ', len(messages))
        _from = JID(msg['from']).full
        if self.boundjid.bare not in _from:
            print(_from)
            print(self.boundjid.bare)
            msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def probe(self, probe):
        print('This should be probe: ', probe['type'])
        print(probe)

    def iq(content):
        print(content)
        print('ORIGIN IS: ', content['from'])
        #self.make_iq_result(ito=content['from'], id=['id'], ifrom=self.boundjid.bare  + '/test').send()
        content.reply().send()

    def intamac_device_info(self, info):
        print(info)
        origin = JID(info['from']).bare
        if info['type'] != 'result':
        #self.make_iq_result(id=info['id'], ito=info['from'], ifrom=self.boundjid.bare + '/test').send()
            info.reply().send()
        queue_push(info)

    def intamac_stream(self, stream):
        print(stream)
        origin = JID(stream['from']).bare
        if stream['type'] != 'result':
            stream.reply().send()
        #self.make_iq_result(id=stream['id'], ito=stream['from'], ifrom=self.boundjid.bare + '/test').send()
        

    def intamac_firmware_upgrade(self, upgrade):
        print(upgrade)
        origin = JID(upgrade['from']).bare
        if upgrade['type'] != 'result':
        #self.make_iq_result(id=upgrade['id'], ito=upgrade['from'], ifrom=self.boundjid.bare + '/test').send()
            upgrade.reply().send()

    def intamac_api(self, api):
        print(api)
        origin = JID(api['from']).bare
        if api['type'] != 'result':
        #self.make_iq_result(id=api['id'], ito=api['from'], ifrom=self.boundjid.bare + '/test').send()
            api.reply().send()

    def intamac_event(self, event):
        print(event)
        origin = JID(event['from']).bare
        if event['type'] != 'result':
        #self.make_iq_result(id=event['id'], ito=event['from'], ifrom=self.boundjid.bare + '/test').send()
            event.reply().send()

    def delay(self, delay):
        '''
        This method has to be properly configured to send a notification straight to the database
        letting it know that the respective device is online.
        '''
        print(delay)

    def poll_queue(self, queue=None):
        pass



    #############################################
    ## CODE FOR COMMUNICATION WITH THE DEVICES ##
    #############################################

    def intamac_firmware_upgrade(self):
        upgrade = IntamacFirmwareUpgrade()
        upgrade['location'] = "https://stg.upgrade.swann.intamac.com/swa_firmware_v505_151020.dav"
        #print(upgrade)
        iqs = [self.make_iq_set(sub=upgrade, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp 

    def intamac_api(self):
        text = '&lt;SoundPackList&gt;&lt;SoundPack&gt;&lt;tag&gt;Aggression&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;BabyCry&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;CarAlarm&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;GlassBreak&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;Gunshot&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;SoundPack&gt;&lt;tag&gt;SmokeAlarm&lt;/tag&gt;&lt;enabled&gt;false&lt;/enabled&gt;&lt;sensitivity&gt;50&lt;/sensitivity&gt;&lt;/SoundPack&gt;&lt;/SoundPackList&gt;'
        text2 = '<SoundPackList><SoundPack><tag>Aggression</tag><enabled>false</enabled><sensitivity>100</sensitivity></SoundPack><SoundPack><tag>BabyCry</tag><enabled>false</enabled><sensitivity>50</sensitivity></SoundPack><SoundPack><tag>CarAlarm</tag><enabled>true</enabled><sensitivity>50</sensitivity></SoundPack><SoundPack><tag>GlassBreak</tag><enabled>true</enabled><sensitivity>50</sensitivity></SoundPack><SoundPack><tag>Gunshot</tag><enabled>false</enabled><sensitivity>50</sensitivity></SoundPack><SoundPack><tag>SmokeAlarm</tag><enabled>false</enabled><sensitivity>50</sensitivity></SoundPack></SoundPackList>'
        api = IntamacAPI(param=text2, url="/Event/audioanalyse", type='1', soundpacklist=False)
        #api['SoundPackList']['SoundPack']['enabled'] = 'True'
        #print(api)
        iqs = [self.make_iq_set(sub=api, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp 

    def intamac_stream(self):
        stream = IntamacStream('000000000000000000000000000000000000000000000000000000000000', 
            ip='192.168.1.100', 
            port='5000', 
            type='start', 
            timeout='10', 
            quality='sub')
        #print(stream)
        iqs = [self.make_iq_set(sub=stream, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp       



def presses(xmpp):
    while True:
        key = input('Enter command: ')
        if key == 'send_iq':
            xmpp.iq_send()
        if key == 'subscribe':
            xmpp.send_subscriptions()
        if key == 'send_message':
            xmpp.bot_message()
        if key == 'unsubscribe':
            xmpp.send_unsubscriptions()
        if key == 'chat':
            xmpp.chat_send()
        if key == 'message':
            xmpp.bot_message()
        if key == 'disconnect':
            xmpp.disconnect()
        if key == 'stream':
            xmpp.intamac_stream()
        if key == 'upgrade':
            xmpp.intamac_firmware_upgrade()
        if key == 'api':
            xmpp.intamac_api()
        if key == 'ping':
            xmpp.intamac_ping()
        if key == 'event':
            xmpp.intamac_event()
        if key == 'info':
            xmpp.device_info()

if __name__ == '__main__':

    def exit_handler():
        xmpp.disconnect()

    atexit.register(exit_handler)

    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    # Load configuration data.
    config_file = open('config.xml', 'r+')
    config_data = "\n".join([line for line in config_file])
    config = Config(xml=ET.fromstring(config_data))
    config_file.close()

    xmpp = ConfigComponent(config)   
    xmpp.registerPlugin('xep_0030') # Service Discovery
    xmpp.registerPlugin('xep_0004') # Data Forms
    xmpp.registerPlugin('xep_0060') # PubSub
    xmpp.registerPlugin('xep_0199') # XMPP Ping
    xmpp.registerPlugin('xep_0203') # Delayed stanzas

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(block=False)
        thread2 = threading.Thread(target=presses, args=(xmpp,))
        thread2.start()
        print("Done")
    else:
        print("Unable to connect.")

