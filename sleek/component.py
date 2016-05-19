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

from custom_stanzas import IntamacHandler, Config


register_stanza_plugin(Config, Roster)
register_stanza_plugin(Iq, IntamacHandler)



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

        path = '{%s}%s' % (IntamacHandler.namespace, IntamacHandler.name)
        print('THE PATH IS THIS: ', path)
        
        self.register_handler(
            Callback('iq_intamacdeviceinfo',
                StanzaPath('iq@type=set/iq_intamacdeviceinfo'),
                self.intamac_device_info))

        
        # Store the roster information.
        #self.roster = roster.Roster(self)
        #self.roster.add(self.boundjid)
        #print('First roster: ', self.roster)
        #self.roster = config['roster']['item']
        #print('Roster: ', self.roster)

        # The session_start event will be triggered when
        # the component establishes its connection with the
        # server and the XML streams are ready for use. We
        # want to listen for this event so that we we can
        # broadcast any needed initial presence stanzas.
        self.add_event_handler("session_start", self.start, threaded=True)
        self.add_event_handler('presence', self.presence, threaded=threaded)
        self.add_event_handler('iq_intamacdeviceinfo', self.intamac_device_info, threaded=True)
        if option == 'unsubscribe':
            print('on unsubscribe mode')
            pass
        else: 
            print('adding other handlers')
            self.add_event_handler('presence_subscribe', self.subscribe, threaded=threaded)
            self.add_event_handler('presence_subscribed', self.subscribed, threaded=threaded)    
            #self.add_event_handler('stream', self.stream)
            self.add_event_handler('presence_probe', self.probe, threaded=threaded)


        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        self.add_event_handler("message", self.message, threaded=threaded)
        self.add_event_handler('iq', self.iq, threaded=True)
        print(self.boundjid)
        #self.add_event_handler('roster_subscription_request', self.roster_subscription_request, threaded=True)

        #self.auto_authorize = True
        #self.auto_subscribe = True

    def presence(self, presence):
        presences.append(presence)
        print(len(presences))
        print(presence)
        print('TYPE: ', presence['type'])
        _from = JID(presence['from']).bare
        print(_from)
        if _from != 'muc@' + self.boundjid.bare and _from != self.boundjid.bare and _from != 'muc@' + self.boundjid.bare + '/muc' and presence['type'] == 'available':
            self.send_presence(pto=_from, pfrom='muc@' + self.boundjid.bare)
            if option == 'unsubscribe':
                self.send_presence(pto=_from, pfrom='muc@' + self.boundjid.bare , ptype='unsubscribe')
                self.send_presence(pto=_from, pfrom='muc@' + self.boundjid.bare , ptype='unsubscribed')
                #self.send_presence(pto=_from, pfrom='muc@' + self.boundjid.bare, ptype='unsubscribe')
                #self.send_presence(pto=_from, pfrom='muc@' + self.boundjid.bare, ptype='unsubscribed')
        #if _from != 'userx@' + self.boundjid.bare:
        #        self.sendPresence(pto=presence['from'], pfrom=self.boundjid.bare)

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
        # Using the method send_presence() without arguments should just work. The problem
        # is that ejabberd then takes the presence from the component (muc.localhost) and 
        # sends it to itself (muc.localhost), resulting in an error. The error seems to 
        # arise from the fact that a presence is being sent from a JID to the same JID.
        # The solution that I can think of for the moment is to explicitly define 
        # a specific destination and a different sender JID. 
        self.send_presence(pfrom='muc@' + self.boundjid.bare, pto=self.boundjid.bare)
        #self.send_presence(pfrom='muc@' + self.boundjid.bare, pto=self.boundjid.bare)
        #self.send_presence(pfrom='muc@' + self.boundjid.bare, pto='user2@use-xmpp-01/test')

    def subscribe(self, presence):
        # If the subscription request is rejected.
        #if not self.backend.allow_subscription(presence['from']):
        #    self.sendPresence(pto=presence['from'], 
        #                      ptype='unsubscribed')
        #    return
         
        # If the subscription request is accepted.
        print('Subscribe: ', presence)
        subscriptions.append(presence)
        print(len(subscriptions))
        print(presence)
        print('This should be subscribe: ', presence['type'])
        self.send_presence_subscription(pto=presence['from'],
                          pfrom='muc@' + self.boundjid.bare)

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
        print('Subscribed: ', presence)
        print(presence)
        print('This should be subscribed: ', presence['type'])
        self.send_presence(pto=presence['from'], pfrom='muc@' + self.boundjid.bare, ptype='subscribed')        
        

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
        #(rc, mid) = cilent.publish("factory/devices/cameras", msg, qos=1)
        msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def probe(self, probe):
        print('This should be probe: ', probe['type'])
        print(probe)

    def iq(self, content):
        print(content)
        self.make_iq_result(ito=content['from'], id=['id'], ifrom='muc@' + self.boundjid.bare).send()

    def intamac_device_info(self, info):
        print(info)
        id = info['id']
        ito = info['from']
        self.make_iq_result(id=id, ito=ito, ifrom='muc@' + self.boundjid.bare).send()

    def roster_subscription_request(self, request):
        print(request)



if __name__ == '__main__':
    option = sys.argv[1]
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
    #mpp.registerPlugin('xep-0198')
    #mpp.registerPlugin('xep-0313')

    

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect():
        print(option)
        xmpp.process(block=False)
        '''
        while True:
            print(len(subscriptions))
            print(len(presences))
            time.sleep(10)
        '''
        print("Done")
    else:
        print("Unable to connect.")




