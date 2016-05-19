#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import getpass
from optparse import OptionParser

import sleekxmpp

if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	raw_input = input
	

class SendMsgBot(sleekxmpp.ClientXMPP):

	def __init__(self, jid, password, recipient, message):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		self.recipient = recipient
		self.msg = message

		self.add_event_handler('session_start', self.start)

	def start(self, event):
		self.send_presence()
		self.get_roster()

		self.send_message(mto=self.recipient, 
						mbody=self.msg,
						mtype='chat')

		self.disconnect(wait=True)

if __name__ == '__main__':
	xmpp = SendMsgBot('user1@localhost', 'mypassword', 'user2@localhost', 'A Message')
	xmpp.register_plugin('xep_0030')
	xmpp.register_plugin('xep_0199')

	if xmpp.connect():
		print('connecting...')
		xmpp.process(block=True)
		print('Done')
	else;
	print('Unable to connect.')

# To run this script do:
# python send_client.py -d -j oneshot@example.com -t someone@example.net -m "This is a message"