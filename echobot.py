#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
import getpass
from optparse import OptionParser
import ssl

import sleekxmpp

if sys.version_info < (3, 0):
	reload(sys)
	sys.setdefaultencoding('utf8')
else:
	raw_input = input

class EchoBot(sleekxmpp.ClientXMPP):
	"""
	A simple SleekXMPP bot taht will echo messages it 
	receives, along with a short thank you message.
	"""

	def __init__(self, jid, password):
		sleekxmpp.ClientXMPP.__init__(self, jid, password)

		# The session_start event will be triggered when
		# the bot establishes its connection with the server
		# and the XML streams are ready for use. We want to
		# listen for this event so that we can initialize
		# our roster. 
		self.add_event_handler('session_start', self.start)

		# The message event is triggered whenever a message
		# stanza is received. Be aware that that includes
		# MUC messages and error messages. 
		self.add_event_handler('message', self.message)

	def start(self, event):
		"""
		Process the session_start event.

		Typical actions for the session_start event are
		requesting the roster and broadcasting an initial
		presence stanza.

		:param event:
			Empty dictionary. The session_start event
			does not provide any additional data.
		:type event:
			`dict`.
		"""

		self.send_presence()
		try:
			self.get_roster()
		except Exception as e:
			print('Exception {} was raised'.format(repr(e)))

	def message(self, msg):
		"""
		Process incoming message stanzas. Be aware that this also
		includes MUC messages and error messages. It is usually
		a good idea to check the messages's type before processing
		or sending replies.

		:param msg:
			The received message stanza. See the documentation for
			stanza objects and the Message stanza to see how it
			may be used.
		:type msg:
			...
		"""

		if msg['type'] in ('normal', 'chat'): #other potential types are error, headline, and groupchat
			msg.reply("Thanks for sending:\n%s" % msg['body']).send() #Can also set msg['to'] parameter


if __name__ == '__main__':
	# Setup the command line arguments.
	optp = OptionParser()

	# Output verbosity options. 
	optp.add_option('-q', '--quit', help='set logging to ERROR',
						action='store_const', dest='loglevel',
						const=logging.ERROR, default=logging.INFO)
	optp.add_option('-d', '--debug', help='set logging to DEBUG',
						action='store_const', dest='loglevel',
						const=logging.DEBUG, default=logging.INFO)
	optp.add_option('-v', '--verbose', help='set logging to COMM',
						action='store_const', dest='loglevel',
						const=5, default=logging.INFO)

	# JID and password options. 
	optp.add_option('-j', '--jid', dest='jid',
						help='JID to use')

	optp.add_option('-p', '--password', dest='password',
						help='password to use')

	opts, args = optp.parse_args()

	# Setup logging
	logging.basicConfig(level=opts.loglevel,
						format='%(levelname)-8s %(message)s')

	if opts.jid is None:
		opts.jid = raw_input('Username: ')
	if opts.password is None:
		opts.password = getpass.getpass('Password: ')

	# Setup the EchoBot and register plugins. Note that while plugins may
	# have interdependencies, the order in which you register them does
	# not matter. 
	xmpp = EchoBot(opts.jid, opts.password)
	xmpp.register_plugin('xep_0030') # Service Discovery
	xmpp.register_plugin('xep_0004') # Data form
	xmpp.register_plugin('xep_0060') # PubSub
	xmpp.register_plugin('xep_0199') # XMPP Ping

	# Possible requirement to connect to OpenFire server...
	xmpp.ssl_version = ssl.PROTOCOL_SSLv23

	if xmpp.connect():
		# If you do not have the dnspython library installed, you will need
		# to manually specify the name of the server if it does not match
		# the one in the JID. For example, to use Google Talk you would 
		# need to use:
		# 
		# if xmpp.connect('talk.google.com', 5222):
		# 	... 
		xmpp.process(block=True)
		print('Done')
	else:
		print('Unable to connect')


# to run the script:
# python echobot.py -d -j something@example.com 


