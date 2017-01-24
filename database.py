from psycopg2 import pool

class Database:
	__connection_pool = None

	@staticmethod
	def initialise(**kwargs):
		Database.__connection_pool = pool.SimpleConnectionPool(1, 10, **kwargs)

	@classmethod
	def get_connection(cls):
		return cls.__connection_pool.getconn()

	@classmethod
	def return_connection(cls, connection):
		Database.__connection_pool.putconn(connection)

	@classmethod
	def close_all_connections(cls):
		Database.__connection_pool.close_all()

class CursorFromConnectionFromPool:
	def __init__(self):
		self.connection = None
		self.cursor = None

	def __enter__(self):
		self.connection = Database.get_connection()
		self.cursor = self.connection.cursor()
		return self.cursor

	def __exit__(self, exception_type, exception_value, exception_traceback):
		if exception_value is not None:
			self.connection.rollback() #if there is a value in the error, do the rollback
		else:
			self.cursor.close()
			self.connection.commit()
		Database.return_connection(self.connection)

#this is for making one connection a time
#import psycopg2
#def connect():
#	return psycopg2.connect(user='postgres', password='sancas', database='learning', host='localhost')
