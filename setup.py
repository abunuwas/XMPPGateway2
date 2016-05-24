from distutils.core import setup
setup(name='XMPPGateway',
		version='1.0',
		description='Scalable Python implementation of an XMPP Component connection using SleekXMPP library.',
		author='Jose Haro, Robert butler',
		author_email='joseh@intamac.com, robertb@intamac.com',
		url='',
		license='',
		py_modules=['sleek', 'sleek.custom_stanzas', 'queueing', 'queueing.stream'],
		)