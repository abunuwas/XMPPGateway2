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

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')


class Config(ElementBase):

    """
    In order to make loading and manipulating an XML config
    file easier, we will create a custom stanza object for
    our config XML file contents. See the documentation
    on stanza objects for more information on how to create
    and use stanza objects and stanza plugins.

    We will reuse the IQ roster query stanza to store roster
    information since it already exists.

    Example config XML:
      <config xmlns="sleekxmpp:config">
        <jid>component.localhost</jid>
        <secret>ssshh</secret>
        <server>localhost</server>
        <port>8888</port>

        <query xmlns="jabber:iq:roster">
          <item jid="user@example.com" subscription="both" />
        </query>
      </config>
    """

    name = "config"
    namespace = "sleekxmpp:config"
    interfaces = set(('jid', 'secret', 'server', 'port'))
    sub_interfaces = interfaces


registerStanzaPlugin(Config, Roster)


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
                                     config['port'])

        # Store the roster information.
        self.roster = roster.Roster(self)
        self.roster.add(self.boundjid)
        print('First roster: ', self.roster)
        #self.roster = config['roster']['item']
        #print('Roster: ', self.roster)

        # The session_start event will be triggered when
        # the component establishes its connection with the
        # server and the XML streams are ready for use. We
        # want to listen for this event so that we we can
        # broadcast any needed initial presence stanzas.
        self.add_event_handler("session_start", self.start)
        self.add_event_handler('presence_subscribe', self.subscribe)
        self.add_event_handler('presence_subscribed', self.subscribed)
        self.add_event_handler('presence', self.presence)


        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message)
        print(self.boundjid.bare)
        self.add_event_handler('iq', self.iq)

        #self.auto_authorize = True
        #self.auto_subscribe = True

    def presence(self, presence):
        print(presence)
        self.sendPresence(pto=presence['from'], pfrom=self.boundjid.bare)
        #if not presence['type'] == 'unavailable' and presence['from'] != 'test.use-xmpp-01':
        #    self.sendPresence(pto=presence['from'])

    def start(self, event):
        """
        Process the session_start event.

        The typical action for the session_start event in a component
        is to broadcast presence stanzas to all subscribers to the
        component. Note that the component does not have a roster
        provided by the XMPP server. In this case, we have possibly
        saved a roster in the component's configuration file.

        Since the component may use any number of JIDs, you should
        also include the JID that is sending the presence.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        '''
        for jid in self.roster:
            if self.roster[jid]['subscription'] != 'none':
                self.sendPresence(pfrom=self.jid, pto=jid)
        '''
        #self.send_presence(pto='use-xmpp-01', pfrom='test.use-xmpp-01')
        #self.sendPresence(pto='test.use-xmpp-01', ptype='available')
        self.sendPresence(pfrom=self.boundjid.bare, pto='use-xmpp-01')
        self.sendPresenceSubscription(pfrom=self.boundjid.bare, pto='use-xmpp-01')
        self.sendPresenceSubscription(pto='user1@localhost', ptype='subscribe', pfrom='userx@muc.localhost')
        #self._start_thread('chat_send', self.chat_send)
        print(event)
        #self.sendPresence(pfrom='user1@localhost')

    def subscribe(self, presence):
        # If the subscription request is rejected.
        #if not self.backend.allow_subscription(presence['from']):
        #    self.sendPresence(pto=presence['from'], 
        #                      ptype='unsubscribed')
        #    return
         
        # If the subscription request is accepted.
        print(presence)
        self.sendPresence(pto=presence['from'],
                          ptype='subscribed')

        # Save the fact that a subscription has been accepted, somehow. Here
        # we use a backend object that has a roster.
        #self.backend.roster.subscribe(presence['from'])

        # If a bi-directional subscription does not exist, create one.
        #if not self.backend.roster.sub_from(presence['from']):
        #    self.sendPresence(pto=presence['from'],
        #                      ptype='subscribe')

    def subscribed(self, presence):
        # Store the new subscription state, somehow. Here we use a backend object.
        #self.backend.roster.subscribed(presence['from'])

        # Send a new presence update to the subscriber.
        print(presence)
        self.sendPresenceSubscription(pto=presence['from'])        
        

    def message(self, msg):
        """
        Process incoming message stanzas. Be aware that this also
        includes MUC messages and error messages. It is usually
        a good idea to check the messages's type before processing
        or sending replies.

        Since a component may send messages from any number of JIDs,
        it is best to always include a from JID.

        Arguments:
            msg -- The received message stanza. See the documentation
                   for stanza objects and the Message stanza to see
                   how it may be used.
        """
        # The reply method will use the messages 'to' JID as the
        # outgoing reply's 'from' JID.
        
        print(msg)
        msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def iq(self, content):
        print(content)
        content.reply('Thanks for sending iq').send()


    def chat_send(self):
        while True:
            self.send_message('user2@localhost', 'THIS IS A MESSAGE', 'chat', 'muc.localhost')
            time.sleep(5)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(levelname)-8s %(message)s')

    # Load configuration data.
    config_file = open('config.xml', 'r+')
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