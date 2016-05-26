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
import getpass
from optparse import OptionParser
import ssl
import time
from sleekxmpp.stanza.iq import Iq
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin
from sleekxmpp.xmlstream import ElementBase, StanzaBase
from sleekxmpp.exceptions import IqTimeout, IqError

from custom_stanzas import IntamacHandler


strings = '&lt;xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;&gt;&lt;DeviceInfo version=&quot;1.0&quot;&gt;&lt;deviceName&gt;IP CAMERA&lt;/deviceName&gt;&lt;deviceID&gt;88&lt;/deviceID&gt;&lt;deviceDescription&gt;IPCamera&lt;/deviceDescription&gt;&lt;deviceLocation&gt;STD-CGI&lt;/deviceLocation&gt;&lt;systemContact&gt;STD-CGI&lt;/systemContact&gt;&lt;model&gt;SWO-SVC01K&lt;/model&gt;&lt;serialNumber&gt;SWO-SVC01K0120150427CCRR516288616&lt;/serialNumber&gt;&lt;macAddress&gt;bc:51:fe:83:27:7d&lt;/macAddress&gt;&lt;firmwareVersion&gt;V5.0.5&lt;/firmwareVersion&gt;&lt;firmwareReleasedDate&gt;151020&lt;/firmwareReleasedDate&gt;&lt;bootVersion&gt;V1.3.4&lt;/bootVersion&gt;&lt;bootReleasedDate&gt;100316&lt;'



#registerStanzaPlugin(Iq, IntamacHandler)

#Iq.interfaces.add('intamacdeviceinfo')
#Iq.sub_interfaces.add('intamacdeviceinfo')

class EchoBot(sleekxmpp.ClientXMPP):

	def __init__(self, jid, password):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.add_event_handler('session_start', self.start, threaded=True)

		self.add_event_handler('message', self.message)

		self.add_event_handler('presence_subscribe', self.subscribe)
		self.add_event_handler('presence_subscribed', self.subscribed)
		#self.add_event_handler('presence', self.presence)

	def start(self, event):
		self.send_presence(pto='muc@test.use-xmpp-01')
		#self.send_presence(pfrom=self.boundjid.bare, pto='muc@test.use-xmpp-01', ptype='subscribe')
		#self.send_presence(pfrom=self.boundjid.bare, pto='muc@muc.localhost', ptype='subscribe')
		roster = self.get_roster()
		#self.update_roster('muc@test.use-xmpp-01/muc', subscription='both')
		print('THIS IS THE ROSTER: ', self.roster)
		#self.chat_send()
		self.iq_send()

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
		while True:
			self.send_message(mfrom=self.boundjid.bare, mbody='THIS IS A MESSAGE', 
				mtype='chat', mto='test.use-xmpp-01')
			time.sleep(5)

	def make_send_iq(self):
		device_info = IntamacHandler(strings)
		iq = self.make_iq_set(sub=device_info, ito='user1@use-xmpp-01/test', ifrom=self.boundjid.bare)
		#print('printing IQ')
		#print('IQ: ', iq)
		resp = iq.send(timeout=5)
		return resp

	def iq_send(self):
		#device_info = IntamacHandler(strings)
		#device_info['intamacdeviceinfo'] = strings
		#device_info.add_param(strings)
		#ET.register_namespace('', 'intamac:intamacdeviceinfo')
		#root = ET.Element('{intamac:intamacdeviceinfo}intamacdeviceinfo')
		#root.text = strings
		#tree = ET.ElementTree(root)
		#iq = self.make_iq_set(sub=device_info, ito='muc@test.use-xmpp-01/muc', ifrom=self.boundjid.bare)
		#iq['intamacdeviceinfo'] = IntamacHandler()
		#iq['intamacdeviceinfo'].text = strings
		#iq['intamacdeviceinfo'].namespace = 'intamac:intamacdeviceinfo'
		while True:
			try:
				resp = self.make_send_iq()
				print(resp)
			except IqError as e:
				print(str(e))
			except IqTimeout as e:
				print(str(e))
			time.sleep(5)


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

	import multiprocessing as mp
	from multiprocessing import Process, Pipe, Array, Manager, Pool

	jobs = []
	for i in range(2):
		process = mp.Process(target=make_bot, args=('user' + str(i),))
		jobs.append(process)

	for job in jobs:
		job.start()

	#for job in jobs:
	#	job.join()




