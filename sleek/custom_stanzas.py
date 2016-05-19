#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sleekxmpp.xmlstream.stanzabase import ET
from sleekxmpp.xmlstream import ElementBase


class DeviceInfo(ElementBase):
    namespace = 'intamac:intamacdeviceinfo'
    name = 'intamacdeviceinfo'
    plugin_attrib = 'iq_intamacdeviceinfo'
    
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
    types = set(('start', 'stop'))
    quality = set(('main', 'sub'))

    def __init__(self, param=None, *args, **kwargs):
        ET.register_namespace('', 'intamac:intamacstream')
        root = ET.Element('{intamac:intamacstream}intamacstream')
        root.text = param
        ElementBase.__init__(self, xml=root)
        for key in kwargs:
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