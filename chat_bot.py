import sys
import logging
import getpass
from optparse import OptionParser
import ssl
import time

import sleekxmpp



class EchoBot(sleekxmpp.ClientXMPP):

	def __init__(self, jid, password):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.add_event_handler('session_start', self.start)

		self.add_event_handler('message', self.message)

	def start(self, event):
		self.send_presence()
		roster = self.get_roster()
		print(roster)
		self.chat_send()

	def message(self, msg):
		print(msg)
		if msg['type'] in ('chat', 'normal'):
			msg.reply('Thanks for sending\n%(body)s' % msg).send()

	def chat_send(self):
		while True:
			self.send_message(mfrom=self.boundjid.bare, mbody='THIS IS A MESSAGE', 
				mtype='chat', mto='muc.localhost')
			time.sleep(5)

if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')
	xmpp = EchoBot('user2@localhost', 'mypassword')
	#xmpp.ssl_version = ssl.PROTOCOL_SSLv3
	if xmpp.connect(('127.0.0.1', 5222)):
		print('connecting...')
		xmpp.process(block=False)
		print('Done')
	else:
		print('Unable to connect')