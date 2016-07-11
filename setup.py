from distutils.core import setup
setup(name='XMPPGateway',
		version='1.0',
		description='Scalable Python implementation of an XMPP Component connection using SleekXMPP library.',
		author='Jose Haro, Robert Butler',
		author_email='joseh@intamac.com, robertb@intamac.com',
		url='',
		license='',
		packages=['sleek', 'db_access', 'queueing_system'],
		py_modules=['sleek.custom_stanzas', 'queueing_system.sqs_q.core_sqs']
		)
