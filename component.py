import sys
import logging
import getpass
from optparse import OptionParser
import ssl

import sleekxmpp
from sleekxmpp.componentxmpp import ComponentXMPP



class EchoBot(ComponentXMPP):

	def __init__(self, jid, password, server, port):
		ComponentXMPP.__init__(self, jid, password, server, port)

		#self.add_event_handler('session_start', self.start)
		self.add_event_handler('message', self.message)

		self.registerPlugin('xep_0077')
		self.plugin['xep_0077'].setForm('username', 'password')
		#self.registerPlugin('feature_mechanisms')
		#self['feature_mechanisms'].unencrypted_plain = True
		self.credentials = {}
		self._stream_feature_handlers = {}
		self._stream_feature_order = []

	'''
	def start(self, event):
		self.send_presence()
		#self.get_roster()
	'''	

	def message(self, msg):
		print(msg)
		msg.reply('Thanks for sending\n%(body)s' % msg).send()


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
	xmpp = EchoBot('muc.localhost', 'secret', '127.0.0.1', '8888')
	xmpp.registerPlugin('xep_0030') # Service Discovery
	xmpp.registerPlugin('xep_0004') # Data Forms
	xmpp.registerPlugin('xep_0060') # PubSub
	xmpp.registerPlugin('xep_0199') # XMPP Ping
	#xmpp.registerPlugin('feature_mechanisms')
	#xmpp['feature_mechanisms'].unencrypted_plain = True
	#xmpp.ssl_version = ssl.PROTOCOL_SSLv3
	if xmpp.connect():
		print('connecting...')
		xmpp.process(block=True)
		print('Done')
	else:
		print('Unable to connect')

