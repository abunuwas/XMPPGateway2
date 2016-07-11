import _mssql
import pymssql
import html
from xml.etree import ElementTree as ET
import datetime
import time

### These parameters must come from config file
server = '192.168.30.20'
user = 'sqluser'
password = '19871n5trumentat10Nabba'
database = 'swa_intamac'

poll_procedure = 'usp_ReceiveCameraCommandNotification'

specific_commands_procedure = {
	'Panel': "exec usp_IntaClimaxG2ControlTableSelect {command_id}",
	'Camera': "exec usp_IntaDMSOutgoingCommandTableSelect '{mac}', {command_id}" 
}

def get_data():
    pass

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

def build_procedure(parameters):
	device = parameters['device']
	bare_procedure = specific_commands_procedure[device]
	full_procedure = bare_procedure.format(**parameters)
	return full_procedure

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

def get_notifications(conn, procedure):
	try:	
		while True:
			result = None
			conn.execute_query(procedure)
			for row in conn:
				result = row[0]
				yield result
	except _mssql.MSSQLDatabaseException:
		yield None

def poll(connection_parameters, poll_procedure):
	conn = get_connection(**connection_parameters)
	conn.query_timeout = 300
	for notification in get_notifications(conn, poll_procedure):
		if notification is not None:
			parameters = process_xml(notification)
			print(parameters)
			full_procedure = build_procedure(parameters)
			print(full_procedure)
			res = conn.execute_row(full_procedure)
			if res is not None:
				command = res['IntaCommand']
				yield command
		else:
			yield None


if __name__ == '__main__':
	connection_parameters = {
							'server': server,
							'user': user,
							'password': password,
							'database': database
							}
	parameters = {
					'mac': 'MacAddress',
					'command_id': 'CommandID',
					'device': 'Camera',
					'command': 'Command'
				}
	#procedure = specific_commands_procedure['Camera']
	#full_procedure = build_procedure(parameters)
	#print(full_procedure)
	for command in poll(connection_parameters, poll_procedure):
		print(command)

