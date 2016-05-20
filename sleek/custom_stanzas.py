#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sleekxmpp.xmlstream.stanzabase import ET
from sleekxmpp.xmlstream import ElementBase


class DeviceInfo(ElementBase):
	namespace = 'intamac:intamacdeviceinfo'
	name = 'intamacdeviceinfo'
	plugin_attrib = 'iq_intamacdeviceinfo'
	default_handler = 'intamac_device_info'
	
	def __init__(self, param=None, *args, **kwargs):
		ET.register_namespace('', 'intamac:intamacdeviceinfo')
		root = ET.Element('{intamac:intamacdeviceinfo}intamacdeviceinfo')
		root.text = param
		ElementBase.__init__(self, xml=root)

'''
	def add_param(self, param):
		ET.register_namespace('', 'intamac:intamacdeviceinfo')
		root = ET.Element('{intamac:intamacdeviceinfo}intamacdeviceinfo')
		root.text = param
		return ET.ElementTree(root)
		#StanzaBase.set_payload(self, param)
'''


class IntamacStream(ElementBase):
	namespace = 'intamac:intamacstream'
	name = 'intamacstream'
	plugin_attrib = 'iq_intamacstream'
	interfaces = set(('ip', 'port', 'type', 'timeout', 'quality'))
	# The two lines below are meant to limit the values that the 
	# elements in the interfaces can take on. However, as of now
	# this functionality is not enabled. 
	types = set(('start', 'stop'))
	quality = set(('main', 'sub'))
	default_handler = 'intamac_stream'

	def __init__(self, param=None, *args, **kwargs):
		ET.register_namespace('', 'intamac:intamacstream')
		root = ET.Element('{intamac:intamacstream}intamacstream')
		root.text = param
		ElementBase.__init__(self, xml=root)
		for key in kwargs:
			if key in self.interfaces:
				self[key] = kwargs[key]
			# Probably the condition should be followed by an else
			# clause to raise an exception or at least log to the 
			# console that an invalid attribute couldn't be set?
			#else:
			#	raise Exception


class IntamacFirmwareUpgrade(ElementBase):
	name = 'intamacfirmwareupgrade'
	namespace = 'intamac:intamacfirmwareupgrade'
	plugin_attrib = 'iq_intamacfirmwareupgrade'
	interfaces = set(('location',))
	default_handler = 'intamac_firmware_upgrade'


class IntamacSetting(ElementBase):
	name = 'intamacsetting'
	namespace = 'intamac:intamacsetting'
	plugin_attrib = 'iq_intamacsetting'
	interfaces = set(('xmppip', 'buddy', 'xmppport', 'eventwait', 'apiport'))
	default_handler = 'intamac_setting'


class IntamacAPI(ElementBase):
	name = 'intamacapi'
	namespace = 'intamac:intamacapi'
	interfaces = set(('url', 'type', 'SoundPackList'))
	plugin_attrib = 'iq_intamacapi'
	sub_interfaces = interfaces
	default_handler = 'intamac_api'

	def __init__(self, tag=None, enabled=None, sensitivity=None, *args, **kwargs):
		# Do we want to make checks on the values passed as parameters for each of
		# these tags? For example, do we want to ensure that enabled is only True
		# or False, or that tag is only one of Aggression, BabyCry, CarAlarm, etc.? 
		ET.register_namespace('', 'intamac:intamacapi')
		root = ET.Element('{intamac:intamacapi}intamacapi')
		sound_pack_list = ET.SubElement(root, 'SoundPackList')
		sound_pack = ET.SubElement(sound_pack_list, 'SoundPack')
		tag_tag = ET.SubElement(sound_pack, 'tag')
		tag_tag.text = tag
		tag_enabled = ET.SubElement(sound_pack, 'enabled')
		tag_enabled.text = enabled
		tag_sensitivity = ET.SubElement(sound_pack, 'sensitivity')
		tag_sensitivity.text = sensitivity
		ElementBase.__init__(self, xml=root)


class IntamacEvent(ElementBase):
	name = 'intamacevent'
	namespace = 'intamac:intamacevent'
	plugin_attrib = 'iq_intamacevent'
	interfaces = set(('type', 'sequence', 'description'))
	default_handler = 'intamac_event'

	def __init__(self, event=None, *args, **kwargs):
		ET.register_namespace('', 'intamac:intamacevent')
		root = ET.Element('{intamac:intamacevent}intamacevent')
		root.text = event
		ElementBase.__init__(self, xml=root)
		for key in kwargs:
			if key in self.interfaces:
				self[key] = kwargs[key]



class Config(ElementBase):

	"""
	In order to make loading and manipulating an XML config
	file easier, we will create a custom stanza object for
	our config XML file contents. See the documentation
	on stanza objects for more information on how to create
	and use stanza objects and stanza plugins.

	We will reuse the IQ roster query stanza to store roster
	information since it already exists.

	Example config XML:
	  <config xmlns="sleekxmpp:config">
		<jid>component.localhost</jid>
		<secret>ssshh</secret>
		<server>localhost</server>
		<port>8888</port>

		<query xmlns="jabber:iq:roster">
		  <item jid="user@example.com" subscription="both" />
		</query>
	  </config>
	"""

	name = "config"
	namespace = "sleekxmpp:config"
	interfaces = set(('jid', 'secret', 'server', 'port'))
	sub_interfaces = interfaces
	default_handler = ''