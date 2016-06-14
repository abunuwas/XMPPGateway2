import os
import atexit
import logging
from xml.etree import ElementTree as ET
from XMPPGateway.sleek.component import Component
from XMPPGateway.sleek.custom_stanzas import Config

cd = os.getcwd()
config_dir = os.path.abspath(os.path.join(cd, 'config'))
local_config_file = os.path.join(config_dir, 'config_local.xml')
prod_config_file = os.path.join(config_dir, 'config.xml')

xmpp = None

def exit_handler():
    if xmpp is not None:
        xmpp.disconnect()

atexit.register(exit_handler)

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(message)s')
boto_logger = logging.getLogger('botocore')
boto_logger.setLevel(logging.ERROR)

# Load configuration data.
config_file = open(prod_config_file, 'r+')
config_data = "\n".join([line for line in config_file])
config = Config(xml=ET.fromstring(config_data))
config_file.close()

xmpp = Component(config)

# Connect to the XMPP server and start processing XMPP stanzas.
if xmpp.connect():
    xmpp.process(block=False)
    thread2 = threading.Thread(args=(xmpp,))
    thread2.start()
    print("Done")
else:
    print("Unable to connect.")

