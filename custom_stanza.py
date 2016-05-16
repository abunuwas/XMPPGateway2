import sleekxmpp
from sleekxmpp.xmlstream.stanzabase import ElementBase, ET, JID
from sleekxmpp.stanza.iq import Iq

class IntamacHandler(ElementBase):
    namespace = 'intamac:intamacdeviceinfo'
    name = 'intamacdeviceinfo'
    plugin_attrib = 'iq_intamacdeviceinfo'
    interfaces = set(('name', 'value')) # not needed I think in principle
    sub_interfaces = interfaces
