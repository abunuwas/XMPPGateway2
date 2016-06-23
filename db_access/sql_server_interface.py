import _mssql
import pymssql
import html
from xml.etree import ElementTree as ET
import datetime
import time

server = '192.168.30.20'
user = 'sqluser'
password = '19871n5trumentat10Nabba'
database = 'swa_intamac'

procedures = {
	'Camera_Command': 'usp_IntaDMSOutgoingCommandTableSelect'
}

specific_commands_procedure = {
	'Panel': "usp_IntaDMSOutgoingCommandTableSelect {command_id}",
	'Camera': "usp_IntaClimaxG2ControlTableSelect '{mac}' {command_id}" 
}

def build_camera_procedure(parameters):
	'''
	CHECK THAT THIS WORKS!!
	'''
	device = parameters['device']
	bare_procedure = specific_commands_procedure[device]
	full_procedure = bare_procedure.format(**parameters)
	return full_procedure

def get_token(outcomes):
	try:
		token = outcomes['command'] + '_' + outcomes['device']
		return token
	except IndexError:
		print('Invalid outcomes object')

def get_procedure(token):
	try:
		procedure = procedures[token]
		return procedure
	except IndexError:
		print('Token not defined')

def build_procedure(outcomes):
	token = get_token(outcomes)
	bare_procedure = get_procedure(token)
	full_procedure = "exec {}, '{}' {}".format(bare_procedure, )

def get_connection(server=None, user=None, password=None, database=None):
	conn = _mssql.connect(server=server, 
							user=user, 
							password=password, 
							database=database
							)
	return conn

def xml_unscape(raw_xml):
	xml_string = html.unescape(raw_xml)
	return xml_string

def xml_build(xml_string):
	xml = ET.fromstring(xml_string)
	return xml

def get_parameters(xml):
	try:
		command = xml.findall('NotificationType')[0].text
		device = xml.findall('DeviceType')[0].text
		data = xml.findall('Data')[0]
		sql_notification_command = data.findall('SQLNotificationCommand')[0]
		mac = sql_notification_command.findall('MACAddress')[0].text
		command_id = sql_notification_command.findall('ControlCommandID')[0].text
		outcome = {
					'command': command,
					'device': device,
					'mac': mac,
					'command_id': command_id
					}
		return outcome
	except IndexError:
		return None

def process_xml(data):
	'''
	Helper function which processes the XML body of commands from the platform
	to the devices and returns a dictionary with the parameters. 
	'''
	xml_string = html.unescape(data)
	xml = ET.fromstring(xml_string)
	parameters = get_parameters(xml)
	return parameters

def get_notifications(conn):
	pass 

def poll(connection_parameters, stored_procedure=None):
	conn = get_connection(**connection_parameters)
	try:
		conn.query_timeout = 1
		while True:
			outcome = None
			conn.execute_query(stored_procedure)
			for row in conn:
				outcome = process_xml(data=row[0])
				yield get_data(conn, outcome)
	except _mssql.MSSQLDatabaseException:
		yield None
		conn.close
		poll(connection_parameters, stored_procedure)

def get_data(conn, stored_procedure=None, parameter=''):
	#conn = _mssql.connect(**connection_parameters)
	procedure = build_procedure(outcomes)
	res = conn.execute_row(stored_procedure)
	if res is not None:
		command = res['IntaCommand']
		#conn.close()
		return command
	else: print('**************************************Nothing to send')
	#conn.close()

if __name__ == '__main__':
	#conn = get_connection(server=server, user=user, password=password, database=database)
	#conn.close()
	#print(conn)
	#conn = get_connection(server=server, user=user, password=password, database=database)
	connection_parameters = {
							'server': server,
							'user': user,
							'password': password,
							'database': database
							}
	'''
	e=0
	while e<50:
		print(e)
		outcome = get_data2(connection_parameters, 'usp_ReceiveCameraCommandNotification')
		#print(outcome)
		if outcome is not None and outcome['command'] == 'Command' and outcome['device'] == 'Camera':
			result = get_data3(connection_parameters, 
				"exec usp_IntaDMSOutgoingCommandTableSelect '{}', {}".format(outcome['mac'], outcome['command_id'])) 
			print(result)
			time.sleep(2)
		else: 
			print('-----------------------------------------Nothing to return ')
			print(datetime.datetime.now())
		e+=1
	'''
	parameters = {
					'mac': 'MacAddress',
					'command_id': 'CommandID',
					'device': 'Camera',
					'command': 'Command'
	}
	#procedure = specific_commands_procedure['Camera']
	full_procedure = build_camera_procedure(parameters)
	print(full_procedure)

