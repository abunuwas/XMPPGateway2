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

#logger = logging.getLogger('sleekxmpp')
#logger.setLevel(logging.DEBUG)
#ch = logging.StreamHandler(sys.stdout)
#ch.setLevel(logging.DEBUG)
#formatter = logging.Formatter('%(levelname)-8s %(message)s')
#ch.setFormatter(formatter)
#logger.addHandler(formatter)
#logger.addHandler(ch)

#loggers = logging.Logger.manager.loggerDict
#sleek_log_names = [name for name in loggers if 'sleek' in name]
#sleek_loggers = [logging.getLogger(name) for name in sleek_log_names]
#for log in sleek_loggers:
#	log.setLevel(logging.DEBUG)
#	log.setFormatter(format='%(levelname)-8s %(message)s')
#for log in sleek_loggers:
#	log.setLevel(logging.DEBUG)ls

#sleek_logger = logging.getLogger('xmlstream')
#sleek_logger.setLevel(logging.DEBUG)
#logging.basicConfig(level=logging.DEBUG,
#                    format='%(levelname)-8s %(message)s')
#boto_logger = logging.getLogger('botocore')
#boto_logger.setLevel(logging.ERROR)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('nose').setLevel(logging.WARNING)

# Load configuration data.
config = load_config_data(prod_config_file)

xmpp = Component(config)

# Connect to the XMPP server and start processing XMPP stanzas.
if xmpp.connect():
    xmpp.process(block=False)
    thread2 = threading.Thread(args=(xmpp,))
    thread2.start()
    print("Done")
else:
    print("Unable to connect.")

