import _mssql

def get_connection(server=None, user=None, password=None, database=None):
	conn = _mssql.connect(server=server, 
		user=user, 
		password=password, 
		database=database)

	return conn

def get_data(connection=None, stored_procedure=None):
	with connection as conn:
		data = conn.execute_query(stored_procedure)
		return data

		

