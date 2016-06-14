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


import sys
import logging
import time
from optparse import OptionParser
import threading 
import os

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

from XMPPGateway.sleek.custom_stanzas import (DeviceInfo, 
                                IntamacStream, 
                                IntamacFirmwareUpgrade, 
                                IntamacAPI, 
                                IntamacEvent, 
                                Config
                                )

import atexit 

from XMPPGateway.sleek.component import Component

register_stanza_plugin(Config, Roster)

threaded = True

messages = []

connections = ['c42f90b752dd@use-xmpp-01/camera', 
                'c42f90b752dd@use-xmpp-01', 
                'user0@use-xmpp-01']  

config_dir = os.path.abspath(os.path.join(os.pardir, 'config'))
local_config_file = os.path.join(config_dir, 'config_local.xml')
prod_config_file = os.path.join(config_dir, 'config.xml')

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
    config_file = open(prod_config_file, 'r+')
    config_data = "\n".join([line for line in config_file])
    config = Config(xml=ET.fromstring(config_data))
    config_file.close()

    xmpp = Component(config)   
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
