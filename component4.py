import sys
import logging
import time
from optparse import OptionParser

import sleekxmpp
from sleekxmpp.componentxmpp import ComponentXMPP
from sleekxmpp.stanza.roster import Roster
from sleekxmpp.xmlstream import ElementBase
from sleekxmpp.xmlstream.stanzabase import ET, registerStanzaPlugin

class SimpleBackend:
	pass

class SimpleComponent:
	def __init__(self, jid, password, server, port):
		self.xmpp = sleekxmpp.componentxmpp.ComponentXMPP(jid, password, server, port)
		self.xmpp.add_event_handler("session_start", self.handleXMPPConnected)
		self.xmpp.add_event_handler("changed_subscription",
			self.handleXMPPPresenceSubscription),
		self.xmpp.add_event_handler("got_presence_probe",
			self.handleXMPPPresenceProbe)
		for event in ["message", "got_online", "got_offline", "changed_status"]:
			self.xmpp.add_event_handler(event, self.handleIncomingXMPPEvent)

	def handleXMPPConnected(self, event):
		for user in self.backend.getAllUsers():
			self.xmpp.sendPresence(pto=self.backend.getJIDForUser(user))

	def handleIncomingXMPPEvent(self, event):
		message = event['message']
		user = self.backend.getUserFromJID(event['jid'])
		self.backend.addMessageFromUser(message, user)

	def handleXMPPPresenceProbe(self, event):
		self.xmpp.sendPresence(pto='muc.localhost')

	def handleXMPPPresenceSubscription(self, subscription):
		if subscription['type'] == 'subscribe':
			userJID = subscription['from']
			self.xmpp.sendPresenceSubscription(pto=userJID, ptype='subscribed')
			self.xmpp.sendPresence(pto=userJID)
			self.xmpp.sendPresenceSubscription(pto=userJID, ptype='subscribe')


	def start(self):
		self.xmpp.connect()
		self.xmpp.process()

def main():
	component = SimpleComponent(
		jid='muc.localhost',
		password='secret',
		server='127.0.0.1',
		port=8888)
	component.start()

if __name__ == '__main__':
	main()



