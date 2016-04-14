import sqlite3
import logging
import traceback

LOG_FILENAME = '/tmp/python.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)

f = open('log', 'a')

class Query:

	def __init__(self, args):
		# connect to data base
		self.db = sqlite3.connect(args.db)

		self.users = 'users'
		self.bots = 'bots'
		self.chats = 'chats'
		self.message = 'messages'
		self.cron = 'cron' # once, hour, day, week, month, year

		self.launch()

	def launch(self):
		# Users table
		cursor = self.db.execute("CREATE TABLE IF NOT EXISTS "+self.users+
			" (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"+
			"name VARCHAR(30),"+
			"email VARCHAR(60),"+
			"hash VARCHAR(60) );")

		# Bots table
		cursor = self.db.execute("CREATE TABLE IF NOT EXISTS "+self.bots+
			" (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"+
			"token VARCHAR(30),"+
			"username VARCHAR(30),"+
			"first_name VARCHAR(40),"+
			"bot_id INTEGER,"+
			"user_id INTEGER );")

		# Chats table
		cursor = self.db.execute("CREATE TABLE IF NOT EXISTS "+self.chats+
			" (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"+
			"chat_id INTEGER,"+
			"username VARCHAR(30),"+
			"first_name VARCHAR(30),"+
			"bot_id INTEGER );")

		# Messages table
		cursor = self.db.execute("CREATE TABLE IF NOT EXISTS "+self.message+
			" (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"+
			"chat_id TEXT,"+
			"date VARCHAR(30),"+
			"text TEXT,"+
			"message_id INTEGER,"+
			"bot_id INTEGER);")

		# Crons table
		cursor = self.db.execute("CREATE TABLE IF NOT EXISTS "+self.cron+
			" (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,"+
			"chat_id TEXT,"+
			"enable BOOLEAN,"+
			"date VARCHAR(30),"+
			"repeat VARCHAR(30),"+
			"text TEXT,"+
			"tz_offset INTEGER,"+
			"bot_id INTEGER,"+
			"cron TEXT);")

   	def list_users(self, filter, condition):
   		if( len(filter) > 0 ):
   			filters = []
   			for field in filter:
   				filters.append('{0}="{1}"'.format(field, filter[field]))

   			condition = ' {0} '.format(condition)
   			query = 'SELECT * FROM {0} WHERE {1}'.format(self.users, condition.join(filters))
   		else:
   			query = 'SELECT * FROM {0}'.format(self.users)

   		cursor = self.db.execute(query)

   		return self.cursor_output(cursor)

   	def add_user(self, values):
   		insert = ', '.join('"{0}"'.format(value) for value in values)
   		query = 'INSERT INTO {0} VALUES (null, {1});'.format(self.users, insert)
   		
   		try:
   			cursor = self.db.execute(query)
   			self.db.commit()
   		except:
   			logging.exception('QUERY add_user')
   			raise

   	# 
   	# Universal queries
   	#
   	def cursor_output(self, cursor):
   		output = []

   		for row in cursor:
			row_object = {}
			for index, field in enumerate(row):
				row_object[cursor.description[index][0]] = field
			output.append(row_object)

		return output

   	def list(self, filter, condition, table):
   		if( len(filter) > 0 ):
   			filters = []
   			for field in filter:
   				filters.append('{0}="{1}"'.format(field, filter[field]))

   			condition = ' {0} '.format(condition)
   			query = 'SELECT * FROM {0} WHERE {1}'.format(getattr(self, table), condition.join(filters))

   			if( table == 'message' ):
   				query = 'SELECT {0}.*, (SELECT GROUP_CONCAT(chats.username) FROM chats WHERE messages.chat_id LIKE "%"||chats.chat_id||"%" AND {1}) AS chat FROM {0} WHERE {1} ORDER BY id DESC LIMIT 10'.format(getattr(self, table), condition.join(filters))

   			if( table == 'cron' ):
   				query = 'SELECT {0}.*, (SELECT GROUP_CONCAT(chats.username) FROM chats WHERE cron.chat_id LIKE "%"||chats.chat_id||"%" AND {1}) AS chat FROM {0} WHERE {1} ORDER BY id DESC'.format(getattr(self, table), condition.join(filters))
   		else:
   			query = 'SELECT * FROM {0}'.format(getattr(self, table))

   		cursor = self.db.execute(query)

   		return self.cursor_output(cursor)

   	def insert(self, values, table):
   		input = []
   		def fill(i): return '?'
   		insert = ', '.join(map(fill, values))

   		query = 'INSERT INTO {0} VALUES (null, {1});'.format(getattr(self, table), insert)

   		try:
   			cursor = self.db.execute(query, values)
   			self.db.commit()
   			f.write('[S] insert: \"{0}\", values: \"{1}\" succes\n'.format(query, values))
   			return True
   		except Exception as e:
   			logging.exception('QUERY insert to ', table)
   			f.write('[E] insert: \"{0}\" at table {1} via query \"{2}\", values: \"{1}\"\n'.format(str(e), table, query, values))
   			return False
   			raise

   	def update(self, values, table, id):
   		input = []
   		for key, value in values.iteritems():
   			input.append('{0}=\'{1}\''.format(key, value))
   		update = ', '.join(input)

   		condition = 'id={0}'.format(id);

   		query = 'UPDATE {0} SET {1} WHERE {2};'.format(getattr(self, table), update, condition)

   		try:
   			cursor = self.db.execute(query)
   			self.db.commit()
   			f.write('[S] update: query {0} succes\n'.format(query))
   		except Exception as e:
   			logging.exception('QUERY update to ', table)
   			f.write('[E] update: \"{0}\" at table {1} via query \"{2}\"\n'.format(str(e), table, query))
   			raise

   	def delete(self, table, id):
   		query = 'DELETE FROM {0} WHERE id={1};'.format(getattr(self, table), id)

   		try:
   			cursor = self.db.execute(query)
   			self.db.commit()
   			f.write('[S] delete: query {0} succes\n'.format(query))
   			return True
   		except Exception as e:
   			logging.exception('QUERY update to ', table)
   			f.write('[E] delete: \"{0}\" at table {1} via query \"{2}\"\n'.format(str(e), table, query))
   			return False
   			raise

	def db_close(self):
		self.db.commit()
		self.db.close()