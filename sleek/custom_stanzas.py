#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Intamac Systems Ltd. All Rights Reserved. 
# 
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
:module: sleek.custom_stanzas.
:author: Jose Haro (jharoperalta@intamac.com).
:synopsis: Custom stanza implementations. 
:platforms: Linux and Unix.
:python-version: Python 3. 

This module implements classes that define custom stanza
namespaces which are needed to process correctly the flow 
of communication with the XMPP clients. 

.. WARNING:: The classes below don't follow strictly the expected 
             protocol when building the stanzas. Instead of just 
             relying on the class attributes to achieve that, an 
             initialization method is defined in most of the cases to 
             build the XML of the stanza manually. That does not 
             leverage the functionality inherited from ElementBase.
             An effort should be made later on to make the classes 
             comply with that interface. 
             Additional checks might be included for:
             - Ensuring that all stanzas are built with the right
               parameters.
             - `try`-`except` clauses should be included to catch 
               all sort of potential errors and avoid breaking the
               execution of the program. 
             - Include checks to ensure that, in those cases where
               certain parameters can only take on a specific set 
               of values, users do not assign to them unexpected 
               values. For example, the parameter `quality` in 
               the `IntamacStream` stanza can only take on the 
               values `sub` or `main`, and some checks should be
               included to ensure that only one of those is 
               assigned. 
             - Logging functionality should be enabled. 

Stanza Classes
--------------
.. DeviceInfo
   :namespace: 'intamac:intamacdeviceinfo' # from camera to component, component replies
.. IntamacStream
   :namespace: 'intamac:intamacstream' # from component to camera, and we receive the result reply from camera, streaming blabla
.. IntamacFirmwareUpgrade
   :namespace: 'intamac:intamacfirmwareupgrade' # from component to camera, receive response if it worked or not, normally OK, sometimes API failed...
.. IntamacSetting
   :namespace: 'intamac:intamacsetting' # same, response if it worked or not
.. IntamacAPI
   :namespace: 'intamac:intamacapi' # same, response OK or failed to iq set; when we send get we'll receive the whole string with device activity info
.. IntamacEvent
   :namespace: 'intamac:intamacevent' # from camera to component, normal reply, camera doesn't make checks
.. Config
   :namespace: 'sleekxmpp:config' # 
"""

from sleekxmpp.xmlstream.stanzabase import ET
from sleekxmpp.xmlstream import ElementBase


class DeviceInfo(ElementBase):
    namespace = 'intamac:intamacdeviceinfo'
    name = 'intamacdeviceinfo'
    plugin_attrib = 'iq_intamacdeviceinfo'
    default_handler = 'intamac_device_info'
    
    def __init__(self, param=None, *args, **kwargs):
        '''
        Class constructor that builds the manually
        the XML of the stanza. This procedure is needed
        at the moment to be able to include text into
        the stanza root elements, as the default 
        functionality does not seem to allow that. 
        After defining the XML body of the stanza, 
        ElementBase is initiated passing the body of the
        stanza as an argument for the `xml` parameter
        of the ElementBase class. 
        '''
        ET.register_namespace('', 'intamac:intamacdeviceinfo')
        root = ET.Element('{intamac:intamacdeviceinfo}intamacdeviceinfo')
        root.text = param
        ElementBase.__init__(self, xml=root)


class IntamacStream(ElementBase):
    namespace = 'intamac:intamacstream'
    name = 'intamacstream'
    plugin_attrib = 'iq_intamacstream'
    interfaces = set(('ip', 'port', 'type', 'timeout', 'quality'))
    default_handler = 'intamac_stream'

    def __init__(self, param=None, *args, **kwargs):
        '''
        Class constructor that builds the manually
        the XML of the stanza. This procedure is needed
        at the moment to be able to include text into
        the stanza root elements, as the default 
        functionality does not seem to allow that. 
        After defining the XML body of the stanza, 
        ElementBase is initiated passing the body of the
        stanza as an argument for the `xml` parameter
        of the ElementBase class. 
        '''
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
            #   raise Exception


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
    sub_interfaces = set(('SoundPackList',))
    default_handler = 'intamac_api'

    def __init__(self, 
                soundpacklist=False, 
                tag=None, 
                enabled=None, 
                sensitivity=None, 
                type=None, 
                url=None, 
                param='', 
                *args, 
                **kwargs):
        '''
        Class constructor that builds the manually
        the XML of the stanza. This procedure is needed
        at the moment to be able to include text into
        the stanza root elements, as the default 
        functionality does not seem to allow that. 
        After defining the XML body of the stanza, 
        ElementBase is initiated passing the body of the
        stanza as an argument for the `xml` parameter
        of the ElementBase class. 
        '''
        # Do we want to make checks on the values passed as parameters for each of
        # these tags? For example, do we want to ensure that enabled is only True
        # or False, or that tag is only one of Aggression, BabyCry, CarAlarm, etc.? 
        ET.register_namespace('', 'intamac:intamacapi')
        root = ET.Element('{intamac:intamacapi}intamacapi')
        root.text = param
        if soundpacklist == True:
            sound_pack_list = ET.SubElement(root, 'SoundPackList')
            sound_pack = ET.SubElement(sound_pack_list, 'SoundPack')
            tag_tag = ET.SubElement(sound_pack, 'tag')
            tag_tag.text = tag
            tag_enabled = ET.SubElement(sound_pack, 'enabled')
            tag_enabled.text = enabled
            tag_sensitivity = ET.SubElement(sound_pack, 'sensitivity')
            tag_sensitivity.text = sensitivity
        ElementBase.__init__(self, xml=root)
        self['type'] = type
        self['url'] = url



class IntamacEvent(ElementBase):
    '''
    Class constructor that builds the manually
    the XML of the stanza. This procedure is needed
    at the moment to be able to include text into
    the stanza root elements, as the default 
    functionality does not seem to allow that. 
    '''
    name = 'intamacevent'
    namespace = 'intamac:intamacevent'
    plugin_attrib = 'iq_intamacevent'
    interfaces = set(('type', 'sequence', 'description'))
    default_handler = 'intamac_event'

    def __init__(self, event=None, *args, **kwargs):
        '''
        Class constructor that builds the manually
        the XML of the stanza. This procedure is needed
        at the moment to be able to include text into
        the stanza root elements, as the default 
        functionality does not seem to allow that. 
        After defining the XML body of the stanza, 
        ElementBase is initiated passing the body of the
        stanza as an argument for the `xml` parameter
        of the ElementBase class. 
        '''
        ET.register_namespace('', 'intamac:intamacevent')
        root = ET.Element('{intamac:intamacevent}intamacevent')
        root.text = event
        ElementBase.__init__(self, xml=root)
        for key in kwargs:
            if key in self.interfaces:
                self[key] = kwargs[key]



class Config(ElementBase):

    """
    :author: Nathanael C. Fritz. 
    :source: 
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

    