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

insert_procedure = "usp_IntaDMSOutgoingCommandTableInsert {device}, '{mac}', {command_id}"

def get_connection(server=None, user=None, password=None, database=None):
	conn = _mssql.connect(server=server, 
							user=user, 
							password=password, 
							database=database
							)
	return conn

def push_command(connection_parameters, device='Camera', mac_address='00:1d:94:12:34:56', command_id='5522'):
	conn = get_connection(**connection_parameters)
	full_procedure = insert_procedure.format(device=device, mac=mac_address, command_id=command_id)
	print(full_procedure)

if __name__ == '__main__':
	connection_parameters = {
						'server': server,
						'user': user,
						'password': password,
						'database': database
						}
	push_command(connection_parameters)



