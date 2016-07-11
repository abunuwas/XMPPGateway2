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
import configparser
import threading 
import os

import boto3

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
from sleekxmpp.exceptions import IqTimeout, IqError

from XMPPGateway.queueing_system.sqs_q.core_sqs import get_queue
from XMPPGateway.queueing_system.sqs_q.consumer import poll
from XMPPGateway.queueing_system.sqs_q.producer import push
from XMPPGateway.db_access.sql_server_interface import get_connection, get_data
from XMPPGateway.sleek.custom_stanzas import (DeviceInfo, 
                                IntamacStream, 
                                IntamacFirmwareUpgrade, 
                                IntamacSetting,
                                IntamacAPI, 
                                IntamacEvent, 
                                Config
                                )

import atexit 

threaded = True

class Component(ComponentXMPP):

    def __init__(self, config):


        register_stanza_plugin(Config, Roster)

        ComponentXMPP.__init__(self, config['jid'],
                                     config['password'],
                                     config['server'],
                                     config['port'], use_jc_ns=False)

        # Stanzas sent from the Component to the devices
        self.stanzas = {
                        'intamacapi': IntamacAPI,
                        'intamacstream': IntamacStream,
                        'intamacfirmwareupgrade': IntamacFirmwareUpgrade,
                        'intamacsetting': IntamacSetting,
        }

        # Queue connection objects 
        aws_connection_parameters = {
                                    'aws_access_key_id': config['aws_access_key_id'],
                                    'aws_secret_access_key': config['aws_secret_access_key'],
                                    'region_name': config['region_name']
                                    }
        print('REGION NAMe: ', aws_connection_parameters['region_name'])
        inbound_queue = config['inbound_queue']
        outbound_queue = config['outbound_queue']
        self.inbound = get_queue(inbound_queue, **aws_connection_parameters)
        self.outbound = get_queue(outbound_queue, **aws_connection_parameters)

        custom_stanzas = {
            DeviceInfo: self.intamac_device_info,
            IntamacStream: self.intamac_stream,
            IntamacFirmwareUpgrade: self.intamac_firmware_upgrade,
            IntamacSetting: self.intamac_setting,
            IntamacAPI: self.intamac_api,
            IntamacEvent: self.intamac_event
        }

        for custom_stanza, handler in custom_stanzas.items():
            register_stanza_plugin(Iq, custom_stanza)
            self.register_handler(
                Callback(custom_stanza.plugin_attrib,
                    StanzaPath('iq/{}'.format(custom_stanza.plugin_attrib)),
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

        # The following piece of code shows how is a normal registration
        # process for a single stanza plugin 
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
        self.add_event_handler('presence_subscribe', self.subscribe, threaded=threaded)
        self.add_event_handler('presence_subscribed', self.subscribed, threaded=threaded)  
        #self.add_event_handler('presence_probe', self.probe, threaded=threaded)
        self.add_event_handler('delay', self.delay, threaded=threaded)  
        #self.add_event_handler("message", self.message, threaded=threaded)
        #self.add_event_handler('iq', self.iq, threaded=True)

        # We need a mechanism in place to allow a Component coming online
        # to determine if it's the first connecting Component after a shutdown,
        # or not. 
        if self.check_is_first():
            self.check_status_devices()

        self.registerPlugin('xep_0030') # Service Discovery
        self.registerPlugin('xep_0004') # Data Forms
        self.registerPlugin('xep_0060') # PubSub
        self.registerPlugin('xep_0199') # XMPP Ping
        self.registerPlugin('xep_0203') # Delayed stanzas


    def start(self, event):
        '''
        This method defines the actions taken by the Component once the connection
        to the XMPP server has been verified. 
        '''
        # Using the method send_presence() without arguments should just work. The problem
        # is that ejabberd then takes the presence from the component (muc.localhost) and 
        # sends it to itself (muc.localhost), resulting in an error. The error seems to 
        # arise from the fact that a presence is being sent from a JID to the same JID.
        # The solution that I can think of for the moment is to explicitly define 
        # a specific destination and a different sender JID. 
        self.send_presence(pto='', pfrom=self.boundjid.bare, ptype='probe')
        self.poll_queue(self.inbound)

    def check_status_devices(self):
        '''
        Iterates the iterator returned by obtain_list_devices to check the 
        connection status of every device registered in the platform. 
        '''
        devices = self.obtain_list_devices()

    def obtain_list_devices(self):
        '''
        Queries XXX database to obtain a list of all registered devices. 
        '''
        pass

    def check_is_first(self):
        '''
        Checks whether the current Component is the first connecting Component
        after a shutdown, or whether there currently are other Components 
        connected to the XMPP server. 

        Returns a boolean. 
        '''
        return True

    def presence(self, presence):
        '''
        Handles presence stanzas. 
        '''
        #print(presence)
        '''
        _from = JID(presence['from']).bare
        if self.boundjid.bare not in _from:
            self.send_presence(pto=_from, 
                              pfrom=self.boundjid.bare + '/test', 
                              block=False
                              )
        '''
        pass

    def subscribe(self, presence):
        '''
        Responds to presence subscribe stanzas. 
        '''
        #print(presence)
        self.send_presence(pto=presence['from'],
                          pfrom=self.boundjid.bare + '/test',
                          ptype='available',
                          block=False
                          )

    def subscribed(self, presence):
        '''
        Responds to prseence subscribed stanzas. 
        '''
        print(presence)
        print('This should be subscribed: ', presence['type'])
        self.send_presence(pto=presence['from'], 
                          pfrom=self.boundjid.bare, 
                          ptype='subscribed',
                          block=False
                          )        


    def probe(self, probe):
        '''
        Respond to presence probe stanzas. 
        '''
        #print('This should be probe: ', probe['type'])
        #print(probe)
        pass

    def intamac_device_info(self, info):
        #print(info)
        origin = JID(info['from']).bare
        if info['type'] != 'result':
        #self.make_iq_result(id=info['id'], ito=info['from'], ifrom=self.boundjid.bare + '/test').send(block=False)
            info.reply().send(block=False)
        push(self.outbound, str(info))

    def intamac_stream(self, stream):
        #print(stream)
        origin = JID(stream['from']).bare
        if stream['type'] != 'result':
            stream.reply().send(block=False)
        #self.make_iq_result(id=stream['id'], ito=stream['from'], ifrom=self.boundjid.bare + '/test').send(block=False)
        push(self.outbound, str(stream))
        
    def intamac_firmware_upgrade(self, upgrade):
        #print(upgrade)
        origin = JID(upgrade['from']).bare
        if upgrade['type'] != 'result':
        #self.make_iq_result(id=upgrade['id'], ito=upgrade['from'], ifrom=self.boundjid.bare + '/test').send(block=False)
            upgrade.reply().send(block=False)
        push(self.outbound, str(upgrade))

    def intamac_setting(self, setting):
        #print(setting)
        origin = JID(setting['from']).bare
        if setting['type'] != 'result':
            setting.reply().send(block=False)
        push(self.outbound, str(setting))

    def intamac_api(self, api, *args, **kwargs):
        #print(api)
        push(self.outbound, str(api))
        origin = JID(api['from']).bare
        if api['type'] != 'result':
        #self.make_iq_result(id=api['id'], ito=api['from'], ifrom=self.boundjid.bare + '/test').send(block=False)
            api.reply().send(block=False)

    def intamac_event(self, event):
        #print(event)
        origin = JID(event['from']).bare
        if event['type'] != 'result':
        #self.make_iq_result(id=event['id'], ito=event['from'], ifrom=self.boundjid.bare + '/test').send(block=False)
            event.reply().send(block=False)
        push(self.outbound, str(event))

    def delay(self, delay):
        '''
        This method has to be properly configured to send a notification straight to the database
        letting it know that the respective device is online.
        '''
        print(delay)

    def poll_queue(self, queue_name=None, queue=None):
        #poll_sleep=config['poll_sleep']
        poll_sleep=0
        for data in poll(self.inbound, sleep=poll_sleep):
            #print(data)
            sub_stanza = self.build_sub_stanza(**data)
            iq = self.make_iq_set(sub=sub_stanza, ito=data['to'], ifrom=self.boundjid)
            #print(iq)
            try:
                iq.send(timeout=None)
            except TypeError:
                pass
            except IqTimeout:
                print('It is taking some time to receive back the response...')
            except IqError:
                print('An unexpected error handling the stanza has occurred')
            except Exception as e:
                print('An unexpected error has occurred! ', str(e))


    def build_sub_stanza(self, namespace, **params):
        #print(params)
        sub_stanza = self.stanzas[namespace].__call__(**params)
        return sub_stanza


def load_config_data(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config['DEFAULT']

def make_component(config_path, cls, connect=False, block=False, *args, **kwargs):
    config = load_config_data('config.ini')
    # Create Component instance with config data
    xmpp = cls(config)
    # Connect to the XMPP server and start processing XMPP stanzas.
    if connect:
        xmpp.connect()
        xmpp.process(block=block)
    return xmpp


