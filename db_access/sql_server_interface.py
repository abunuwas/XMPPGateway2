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

def get_connection(server=None, user=None, password=None, database=None):
	conn = pymssql.connect(server=server, 
		user=user, 
		password=password, 
		database=database)
	print(conn)
	return conn

def get_data(connection_parameters, stored_procedure=None, parameter=''):
	with pymssql.connect(**connection_parameters) as conn:
		with conn.cursor(as_dict=True) as cursor:
			print('we are here')
			data = cursor.execute(stored_procedure)
			print('got it')
			for row in cursor:
				print(row)
				'''
				data = row['notification_details']
				data = html.unescape(data)
				xml = ET.fromstring(data)
				command = xml.find('SQLNotificationCommand')
				print(command)
				print(pymssql.output(str))
				'''
			conn.close()
		

def get_data2(connection_parameters, stored_procedure=None, parameter=''):
	conn = _mssql.connect(**connection_parameters)
	conn.query_timeout = 300
	conn.execute_query(stored_procedure)
	outcome = None
	try:
		for row in conn:
			data = row[0]
			data = html.unescape(data)
			#print(data)
			xml = ET.fromstring(data)
			command = xml.findall('NotificationType')[0].text
			#print(command)
			device = xml.findall('DeviceType')[0].text
			#print(device)
			data = xml.findall('Data')[0]
			sql_notification_command = data.findall('SQLNotificationCommand')[0]
			mac = sql_notification_command.findall('MACAddress')[0].text
			#print(mac)
			command_id = sql_notification_command.findall('ControlCommandID')[0].text
			#print(command_id)
			outcome = {
						'command': command,
						'device': device,
						'mac': mac,
						'command_id': command_id
						}
	except IndexError:
		pass
	conn.close()
	return outcome

def get_data3(connection_parameters, stored_procedure=None, parameter=''):
	print(stored_procedure)
	conn = _mssql.connect(**connection_parameters)
	res = conn.execute_row(stored_procedure)
	if res is not None:
		print(res['IntaCommand'])
	else: print('Nothing to send')
	conn.close()

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
	e=0
	while True:
		print(e)
		outcome = get_data2(connection_parameters, 'usp_ReceiveCameraCommandNotification', 'AMI01SB-CVR-001')
		#print(outcome)
		if outcome is not None and outcome['command'] == 'Command' and outcome['device'] == 'Camera':
			result = get_data3(connection_parameters, 
				"exec usp_IntaDMSOutgoingCommandTableSelect '{}', {}".format(outcome['mac'], outcome['command_id'])) 
			time.sleep(2)
		else: 
			print('Nothing to return ')
			print(datetime.datetime.now())
		e+=1
