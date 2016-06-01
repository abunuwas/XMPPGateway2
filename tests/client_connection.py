import sys
import logging
import getpass
from optparse import OptionParser
import ssl
import time

import sleekxmpp
from sleekxmpp.stanza.iq import Iq
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin, register_stanza_plugin
from sleekxmpp.xmlstream import ElementBase, StanzaBase
from sleekxmpp.exceptions import IqTimeout, IqError
from sleekxmpp.stanza.roster import Roster
from sleekxmpp.xmlstream.handler.callback import Callback
from sleekxmpp.xmlstream.matcher import StanzaPath
from sleekxmpp.jid import JID


from custom_stanzas import IntamacHandler, Config


register_stanza_plugin(Config, Roster)
register_stanza_plugin(Iq, IntamacHandler)

threaded = True

messages = []


class EchoBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler('session_start', self.start, threaded=True)

        self.add_event_handler('message', self.message)

        self.add_event_handler('presence_subscribe', self.subscribe)
        self.add_event_handler('presence_subscribed', self.subscribed)
        #self.add_event_handler('presence', self.presence)

        self.register_handler(
            Callback('iq_intamacdeviceinfo',
                StanzaPath('iq@type=set/iq_intamacdeviceinfo'),
                self.intamac_device_info))

        #self.add_event_handler("session_start", self.start, threaded=True)
        #self.add_event_handler('presence', self.presence, threaded=threaded)
        self.add_event_handler('iq_intamacdeviceinfo', self.intamac_device_info, threaded=True)
        #self.add_event_handler('presence_subscribe', self.subscribe, threaded=threaded)
        #self.add_event_handler('presence_subscribed', self.subscribed, threaded=threaded)    
        #self.add_event_handler('presence_probe', self.probe, threaded=threaded)
        self.add_event_handler('iq', self.iq, threaded=True)



    def start(self, event):
        self.send_presence()
        self.get_roster()

    def presence(self, presence):
        print(presence)
        print('TYPE: ', presence['type'])
        _from = JID(presence['from']).bare
        print(_from)
        if self.boundjid.bare not in _from:
            self.send_presence(pto=_from, pfrom=self.boundjid.bare)

    def subscribe(self, presence):
        print(presence)
        print('This should be subscribe: ', presence['type'])
        self.send_presence_subscription(pto=presence['from'])

    def subscribed(self, presence):
        print(presence)
        print('This should be subscribed: ', presence['type'])
        self.send_presence(pto=presence['from'], ptype='subscribed')        
        

    def message(self, msg):
        if self.boundjid.bare not in JID(msg['from']).bare:
            print(msg)
            messages.append(msg)
            print('MESSAGES RECEIVED: ', len(messages))
            #msg.reply("Thanks for sending\n%(body)s" % msg).send()

    def probe(self, probe):
        print('This should be probe: ', probe['type'])
        print(probe)

    def iq(self, content):
        print(content)
        self.make_iq_result(ito=content['from'], id=['id'], ifrom=self.boundjid.bare).send()

    def intamac_device_info(self, info):
        print(info)
        self.make_iq_result(id=id, ito=ito, ifrom=self.boundjid.bare).send()

def make_bot(username):
    xmpp = EchoBot(username + '@use-xmpp-01/test', 'mypassword')
    xmpp.registerPlugin('xep_0030') # Service Discovery
    xmpp.registerPlugin('xep_0004') # Data Forms
    xmpp.registerPlugin('xep_0060') # PubSub
    xmpp.registerPlugin('xep_0199') # XMPP Ping
    if xmpp.connect(('52.71.184.144', 5222), use_tls=True, use_ssl=False):
        print('connecting...')
        xmpp.process(block=True)
        print('Done')
    else:
        print('Unable to connect')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    make_bot('user10')




