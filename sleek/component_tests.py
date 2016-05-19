#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    SleekXMPP: The Sleek XMPP Library
    Copyright (C) 2010  Nathanael C. Fritz
    This file is part of SleekXMPP.

    See the file LICENSE for copying permission.
"""

import sys
import logging
import time
from optparse import OptionParser

import sleekxmpp
from sleekxmpp import roster
from sleekxmpp.componentxmpp import ComponentXMPP
from sleekxmpp.stanza.roster import Roster
from sleekxmpp.xmlstream import ElementBase
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin, register_stanza_plugin
from sleekxmpp.jid import JID
from sleekxmpp.stanza.iq import Iq
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher.xpath import MatchXPath
from sleekxmpp.xmlstream.matcher import StanzaPath

from custom_stanzas import DeviceInfo, Config, IntamacStream

import atexit 


register_stanza_plugin(Config, Roster)
register_stanza_plugin(Iq, DeviceInfo)
register_stanza_plugin(Iq, IntamacStream)

threaded = True

messages = []

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
        
        self.register_handler(
            Callback('iq_intamacdeviceinfo',
                StanzaPath('iq@type=set/iq_intamacdeviceinfo'),
                self.intamac_device_info))

        self.register_handler(
            Callback('iq_intamacstream',
                StanzaPath('iq@type=set/iq_intamacstream'),
                self.intamac_stream))

        #self.add_event_handler("session_start", self.start, threaded=True)
        #self.add_event_handler('presence', self.presence, threaded=threaded)
        self.add_event_handler('iq_intamacdeviceinfo', self.intamac_device_info, threaded=True)
        self.add_event_handler('presence_subscribe', self.subscribe, threaded=threaded)
        self.add_event_handler('presence_subscribed', self.subscribed, threaded=threaded)    
        #self.add_event_handler('presence_probe', self.probe, threaded=threaded)
        self.add_event_handler("message", self.message, threaded=threaded)
        self.add_event_handler('iq', self.iq, threaded=True)

        print('THIS IS THE DEFAULT NS: ', self.default_ns)

    #def incoming_filter(self, xml):
        #print(ET.dump(xml))
        #return xml
        #if xml.tag.startswith('{jabber:client}'):
        #    xml.tag = xml.tag.replace('jabber:client', self.default_ns)
        #return xml

    def presence(self, presence):
        print(presence)
        print('TYPE: ', presence['type'])
        _from = JID(presence['from']).bare
        print(_from)
        if self.boundjid.bare not in _from:
            self.send_presence(pto=_from, pfrom=self.boundjid.bare + '/test')

    def start(self, event):
        # Using the method send_presence() without arguments should just work. The problem
        # is that ejabberd then takes the presence from the component (muc.localhost) and 
        # sends it to itself (muc.localhost), resulting in an error. The error seems to 
        # arise from the fact that a presence is being sent from a JID to the same JID.
        # The solution that I can think of for the moment is to explicitly define 
        # a specific destination and a different sender JID. 
        self.send_presence(pfrom=self.boundjid.bare, pto=self.boundjid.bare + '/test')

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

    def iq(self, content):
        print(content)
        print('ORIGIN IS: ', content['from'])
        self.make_iq_result(ito=content['from'], id=['id'], ifrom=self.boundjid.bare  + '/test').send()

    def intamac_device_info(self, info):
        print(info)
        origin = JID(info['from']).bare
        self.make_iq_result(id=info['id'], ito=info['from'], ifrom=self.boundjid.bare + '/test').send()

    def intamac_stream(self, info):
        print(info)


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

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(block=False)

        print("Done")
    else:
        print("Unable to connect.")




