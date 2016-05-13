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
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin


class Config(ElementBase):

    name = "config"
    namespace = "sleekxmpp:config"
    interfaces = set(('jid', 'secret', 'server', 'port'))
    sub_interfaces = interfaces


registerStanzaPlugin(Config, Roster)


class ConfigComponent(ComponentXMPP):
    def __init__(self, config):

        ComponentXMPP.__init__(self, config['jid'],
                                     config['secret'],
                                     config['server'],
                                     config['port'])

        #self.roster = roster.Roster(self)
        #self.roster.add(self.boundjid)
        #print('First roster: ', self.roster)
        self.roster = config['roster']['item']
        print('Roster: ', self.roster)

        self.add_event_handler("session_start", self.start)
        self.add_event_handler('presence_subscribe', self.subscribe)
        self.add_event_handler('presence_subscribed', self.subscribed)
        self.add_event_handler('presence', self.presence)    
        self.add_event_handler("message", self.message)
        self.add_event_handler('iq', self.iq)

    def start(self, event):
        #self.send_presence(pfrom=self.boundjid.bare, pto='', pstatus='available')
        print('hola')
        self.sendPresence(pfrom=self.boundjid.bare, pto='user1@localhost/test', ptype='subscription')
        self.sendPresence(pfrom=self.boundjid.bare, pto='userx@muc.localhost', ptype='subscription')

    def subscribe(self, presence):
        print('Subscribe: ', presence)
        self.sendPresence(pto=presende['from'], type='subscribed')

    def subscribed(self, presence):
        print('Subscribed: ', presence)
        self.sendPresence(pto=prseence['from'])
        
    def message(self, msg):
        print('MENSAJE: ', msg)

    def iq(self, iq):
        print(iq)

    def presence(self, presence):
        print(presence)

    def stream(self, stream):
        print(stream)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    # Load configuration data.
    config_file = open('config_local.xml', 'r+')
    config_data = "\n".join([line for line in config_file])
    config = Config(xml=ET.fromstring(config_data))
    config_file.close()

    # Setup the ConfigComponent and register plugins. Note that while plugins
    # may have interdependencies, the order in which you register them does
    # not matter.
    xmpp = ConfigComponent(config)
    xmpp.registerPlugin('xep_0030') # Service Discovery
    xmpp.registerPlugin('xep_0004') # Data Forms
    xmpp.registerPlugin('xep_0060') # PubSub
    xmpp.registerPlugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        xmpp.process(threaded=False)
        print("Done")
    else:
        print("Unable to connect.")