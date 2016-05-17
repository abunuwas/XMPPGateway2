import sys
import logging
import getpass
from optparse import OptionParser
import ssl
import time
from sleekxmpp.stanza.iq import Iq
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin
from sleekxmpp.xmlstream import ElementBase


import sleekxmpp

amazon = 'c2-52-71-183-201.compute-1.amazonaws.com'

strings = '&lt;xml version=&quot;1.0&quot; encoding=&quot;UTF-8&quot;&gt;&lt;DeviceInfo version=&quot;1.0&quot;&gt;&lt;deviceName&gt;IP CAMERA&lt;/deviceName&gt;&lt;deviceID&gt;88&lt;/deviceID&gt;&lt;deviceDescription&gt;IPCamera&lt;/deviceDescription&gt;&lt;deviceLocation&gt;STD-CGI&lt;/deviceLocation&gt;&lt;systemContact&gt;STD-CGI&lt;/systemContact&gt;&lt;model&gt;SWO-SVC01K&lt;/model&gt;&lt;serialNumber&gt;SWO-SVC01K0120150427CCRR516288616&lt;/serialNumber&gt;&lt;macAddress&gt;bc:51:fe:83:27:7d&lt;/macAddress&gt;&lt;firmwareVersion&gt;V5.0.5&lt;/firmwareVersion&gt;&lt;firmwareReleasedDate&gt;151020&lt;/firmwareReleasedDate&gt;&lt;bootVersion&gt;V1.3.4&lt;/bootVersion&gt;&lt;bootReleasedDate&gt;100316&lt;'

class IntamacHandler(ElementBase):

	namespace = 'intamac:intamacdeviceinfo'
	name = 'intamacdeviceinfo'
	plugin_attrib = 'iq_intamacdeviceinfo'

	def addParams(self, value):
		param_obj = self(None, self)
		param_obj[self] = value


#registerStanzaPlugin(Iq, IntamacHandler)

class EchoBot(sleekxmpp.ClientXMPP):

	def __init__(self, jid, password):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.add_event_handler('session_start', self.start)

		self.add_event_handler('message', self.message)

	def start(self, event):
		self.send_presence(pfrom=self.boundjid.bare, pto='muc.localhost')
		#self.send_presence(pfrom=self.boundjid.bare, pto='muc@muc.localhost', ptype='subscribe')
		roster = self.get_roster()
		print(roster)
		#self.chat_send()
		self.iq_send()

	def message(self, msg):
		print(msg)
		if msg['type'] in ('chat', 'normal'):
			msg.reply('Thanks for sending\n%(body)s' % msg).send()

	def chat_send(self):
		while True:
			self.send_message(mfrom=self.boundjid.bare, mbody='THIS IS A MESSAGE', 
				mtype='chat', mto='muc.localhost')
			time.sleep(20)

	def iq_send(self):
		device_info = IntamacHandler()
		xml = ET.Element(device_info)
		xml.text = strings
		#xml = ET.tostring(xml)
		print(xml.text)
		print('INSTANCE OF INTAMACHANDLER', device_info)
		print(device_info.parent)
		device_info.addParams(strings)
		iq = self.make_iq_set(sub=device_info, ito='muc@muc.localhost', ifrom=self.boundjid.bare)
		while True:
			print('printing IQ')
			print('IQ: ', iq)
			time.sleep(5)

if __name__ == '__main__':
	logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
	xmpp = EchoBot('user2@use-xmpp-01/test', 'mypassword')
	xmpp.registerPlugin('xep_0030') # Service Discovery
	xmpp.registerPlugin('xep_0004') # Data Forms
	xmpp.registerPlugin('xep_0060') # PubSub
	xmpp.registerPlugin('xep_0199') # XMPP Ping
	#xmpp.ssl_version = ssl.PROTOCOL_SSLv3
	if xmpp.connect(('52.71.183.201', 5222), use_tls=True, use_ssl=False):
		print('connecting...')
		xmpp.process(block=True)
		print('Done')
	else:
		print('Unable to connect')