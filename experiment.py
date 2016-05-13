import sys
import logging
import getpass
from optparse import OptionParser
import ssl

import sleekxmpp



class EchoBot(sleekxmpp.ClientXMPP):

	def __init__(self, jid, password):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.add_event_handler('session_start', self.start)

		self.add_event_handler('message', self.message)

	def start(self, event):
		self.send_presence()
		self.get_roster()

	def message(self, msg):
		print(msg)
		if msg['type'] in ('chat', 'normal'):
			msg.reply('Thanks for sending\n%(body)s' % msg).send()

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
	xmpp = EchoBot('user1@localhost/test', 'mypassword')
	#xmpp.ssl_version = ssl.PROTOCOL_SSLv3
	if xmpp.connect(('127.0.0.1', 5222)):
		print('connecting...')
		xmpp.process(block=True)
		print('Done')
	else:
		print('Unable to connect')

