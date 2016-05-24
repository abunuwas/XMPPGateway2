import sys
import logging
import getpass
from optparse import OptionParser
import ssl
import time

import sleekxmpp
from sleekxmpp.stanza.iq import Iq
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin
from sleekxmpp.xmlstream import ElementBase, StanzaBase
from sleekxmpp.exceptions import IqTimeout, IqError

import atexit

import threading

import curses

from sleek.custom_stanzas import DeviceInfo, IntamacStream, IntamacFirmwareUpgrade, IntamacAPI, IntamacEvent


strings = '&lt;xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;&gt;&lt;DeviceInfo version=&quot;1.0&quot;&gt;&lt;deviceName&gt;IP CAMERA&lt;/deviceName&gt;&lt;deviceID&gt;88&lt;/deviceID&gt;&lt;deviceDescription&gt;IPCamera&lt;/deviceDescription&gt;&lt;deviceLocation&gt;STD-CGI&lt;/deviceLocation&gt;&lt;systemContact&gt;STD-CGI&lt;/systemContact&gt;&lt;model&gt;SWO-SVC01K&lt;/model&gt;&lt;serialNumber&gt;SWO-SVC01K0120150427CCRR516288616&lt;/serialNumber&gt;&lt;macAddress&gt;bc:51:fe:83:27:7d&lt;/macAddress&gt;&lt;firmwareVersion&gt;V5.0.5&lt;/firmwareVersion&gt;&lt;firmwareReleasedDate&gt;151020&lt;/firmwareReleasedDate&gt;&lt;bootVersion&gt;V1.3.4&lt;/bootVersion&gt;&lt;bootReleasedDate&gt;100316&lt;'

connections = ['muc@test2.xmpp.intamac.com/test']

class EchoBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        self.add_event_handler('session_start', self.start, threaded=True)
        self.add_event_handler('message', self.message)
        self.add_event_handler('presence_subscribe', self.subscribe)
        self.add_event_handler('presence_subscribed', self.subscribed)
        #self.add_event_handler('presence', self.presence)

    def start(self, event):
        self.send_presence()
        #self.send_presence(pfrom=self.boundjid.bare, pto='muc@test.use-xmpp-01', ptype='subscribe')
        #self.send_presence(pfrom=self.boundjid.bare, pto='muc@muc.localhost', ptype='subscribe')
        roster = self.get_roster()
        #self.update_roster('muc@test.use-xmpp-01/muc', subscription='both')
        #print('THIS IS THE ROSTER: ', self.roster)
        #self.chat_send()
        #self.iq_send()

    def message(self, msg):
        print(msg)
        if msg['type'] in ('chat', 'normal'):
            msg.reply('Thanks for sending\n%(body)s' % msg).send()

    def subscribe(self, presence):
        print(presence)
        print(presence['type'])
        self.send_presence_subscription(pto=presence['from'], pfrom=self.boundjid.bare)

    def subscribed(self, presence):
        print(presence)
        print(presence['type'])
        self.send_presence_subscribed(pto=presence['from'], pfrom=self.boundjid.bare)

    def presence(self, presence):
        print(presence)
        print(presence['type'])
        self.send_presence(pto=presence['from'], pfrom=self.boundjid.bare)

    def chat_send(self):
        e=0
        while True:
            e+=1
            for conn in connections:
                self.send_message(mfrom=self.boundjid.bare, mbody='THIS IS MESSAGE NUMBER' + str(e), 
                    mtype='chat', mto=conn)
            time.sleep(3)
            print('MESSAGES SENT: ', e)

    def device_info(self):
        device_info = DeviceInfo(strings)
        iqs = [self.make_iq_set(sub=device_info, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp

    def intamac_stream(self):
        stream = IntamacStream('000000000000000000000000000000000000000', 
            ip='192.168.1.100', 
            port='5000', 
            type='start', 
            timeout='10', 
            quality='sub')
        #print(stream)
        iqs = [self.make_iq_set(sub=stream, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp       

    def iqs_send(self):
        while True:
            try:
                resp = self.device_info()
                print(resp)
            except IqError as e:
                print(str(e))
            except IqTimeout as e:
                print(str(e))
            time.sleep(5)

    def iq_send(self):
        try:
            resp = self.device_info()
            print(resp)
        except IqError as e:
            print(str(e))
        except IqTimeout as e:
            print(str(e))
        time.sleep(5)

    def send_subscriptions(self):
        for conn in connections:
            self.send_presence(pto=conn, ptype='subscribe4')

    def bot_message(self):
        for conn in connections:
            self.send_message(mto=conn, mtype='chat', mbody='This is a message')

    def send_unsubscriptions(self):
        for conn in connections:
            self.send_presence(pto=conn, ptype='unsubscribe')

    def intamac_firmware_upgrade(self):
        upgrade = IntamacFirmwareUpgrade()
        upgrade['location'] = "https://stg.upgrade.swann.intamac.com/swa_firmware_v505_151020.dav"
        #print(upgrade)
        iqs = [self.make_iq_set(sub=upgrade, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp 

    def intamac_api(self):
        api = IntamacAPI(enabled='True', tag='SmokeAlarm', sensitivity='50')
        #api['SoundPackList']['SoundPack']['enabled'] = 'True'
        #print(api)
        iqs = [self.make_iq_set(sub=api, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp 

    def intamac_ping(self):
        ping = self['xep_0199'].ping(pto=connections[0])
        #print(ping)

    def intamac_event(self):
        event = IntamacEvent(event='2016-01-07T12:11:38', type='VMD', sequence='72', description='MotionAlarm')
        #print(event)
        iqs = [self.make_iq_set(sub=event, ito=conn, ifrom=self.boundjid.bare) for conn in connections]
        resp = [iq.send(timeout=5) for iq in iqs]
        return resp 


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
    
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

    #thread1 = threading.Thread(target=make_bot, args=('user0',))
    

    xmpp = EchoBot('user0' + '@use-xmpp-01/test', 'mypassword')
    xmpp.registerPlugin('xep_0030') # Service Discovery
    xmpp.registerPlugin('xep_0004') # Data Forms
    xmpp.registerPlugin('xep_0060') # PubSub
    xmpp.registerPlugin('xep_0199') # XMPP Ping
    if xmpp.connect(('52.71.184.144', 5222), use_tls=True, use_ssl=False):
        print('connecting...')
        xmpp.process(block=False)
        thread2 = threading.Thread(target=presses, args=(xmpp,))
        thread2.start()
        print('Done')
    else:
        print('Unable to connect')

    #thread1.start()
    #thread2.start()

    '''
    import multiprocessing as mp
    from multiprocessing import Process, Pipe, Array, Manager, Pool

    jobs = []
    for i in range(2):
        process = mp.Process(target=make_bot, args=('user' + str(i),))
        jobs.append(process)

    for job in jobs:
        job.start()
    '''
