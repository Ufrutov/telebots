import urllib
import urllib2
import json
import time
from datetime import datetime as dt
import string
from query import Query
import telebot
import os
from collections import namedtuple

# import logging

# Pythong global log
# LOG_FILENAME = '/tmp/python.out'
# logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG,)

# f = open('log', 'a')

class Action:

	def __init__(self, args):
		self.telegram = args.telegram
		self.query = Query(args);

	def get_updates(self, bot_id):
		output = {}

		bot = self.query.list({'id': bot_id}, 'AND', 'bots')

		if( len(bot) > 0 ):

			req = urllib2.Request( '{0}{1}/{2}'.format(self.telegram, bot[0]['token'], 'getUpdates') )
			request = urllib2.urlopen(req)
			
			response = json.loads(request.read())
			if( response['ok'] ):
				self.update_chats(response['result'], bot_id)
				output['response'] = response['result']
				output['chats'] = self.query.list({'bot_id': bot_id}, 'AND', 'chats')
				output['ok'] = True			
				output['updates'] = response['result']
			else:
				output['ok'] = False
		else:
			output['ok'] = False

		return output

	def update_chats(self, updates, bot_id):
		chats = {}
		chat_ids = []
		output = []

		for item in updates:
			chat = item['message']['from']['id']
			if( chat not in chat_ids ):
				chats["chat_id"] = item['message']['from']['id']
				chats["username"] = item['message']['from']['first_name']
				chats["first_name"] = item['message']['from']['first_name']
				chats["bot_id"] = bot_id
				chat_ids.append(chats)

		for chat in chat_ids:
			if( len(self.query.list({'chat_id': chat['chat_id'], 'bot_id': bot_id}, 'AND', 'chats')) <= 0 ):
				self.query.insert([chat['chat_id'], chat['username'], chat['first_name'], chat['bot_id']], 'chats')

	def get_message_atr(self, atributes):
		output = {}

		for atr in atributes:
			if( ':' in atr ):
				name = atr.split(':', 1)[0]
				value = atr.split(':', 1)[1]

				output[name] = value

		if( not output ):
			output['error'] = True
			return output
		else:
			output['error'] = False
			return output

	def send_message(self, bot_id, ids, text, tz):
		output = {}
		bot = self.query.list({'id': bot_id}, 'AND', 'bots')

		if( len(bot) > 0 ):
			bot_obj = telebot.TeleBot(str(bot[0]['token']))

			chats = ids.split(',')
			success = []

			for chat in chats:

				try:
					send = bot_obj.send_message(chat, self.convert_text(text, tz, 'request'))
					
					output['send'] = {
						'date': str(send.date),
						'message_id': str(send.message_id)
					}

					output['ok'] = True
					success.append(chat)
				except Exception as e:
					output['status'] = str(e)
					output['ok'] = False

			if( output['ok'] ):
				# message = str(MySQLdb.escape_string( self.convert_text(text, tz, 'save') ))
				message = self.convert_text(text, tz, 'save')
				output['saved'] = self.query.insert([', '.join(success), output['send']['date'], message, output['send']['message_id'], bot_id], 'message')

				output['success'] = success
				output['text'] = text

				return output
			else:
				output['ok'] = False
				output['status'] = 'Message not sent'
		else:
			output['ok'] = False
			output['status'] = 'Bot not found'
		return output

	def convert_text(self, text, tz, action):
		date = int(time.time())-(int(tz)*60*60)

		date = dt.utcfromtimestamp(date).strftime('%H:%M:%S %d/%m/%Y')
		
		output = string.replace(text, '<DATE>', date)

		# if( action == 'request' ):
		return output
		# else:
			# return output.encode('utf8')

	def send_photo(self, bot_id, ids, file_obj, text, tz):
		output = {}

		bot = self.query.list({'id': bot_id}, 'AND', 'bots')
		user = self.query.list({'id': bot[0]['user_id']}, 'AND', 'users')
		# file_Obj = json.loads(file_obj)
		file_Obj = json.loads(file_obj, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))

		directory = file_Obj.folder
		photo = file_Obj.photo

		if( len(bot) > 0 and len(user) > 0 ):
			bot_obj = telebot.TeleBot(str(bot[0]['token']))

			chats = ids.split(',')
			success = []

			path = '{0}/files/{1}/{2}/{3}'.format(os.getcwd(), user[0]['name'], directory, photo)
			photo = open(path)

			for chat in chats:
				try:
					bot_obj.send_photo(chat, photo, self.convert_text(text, tz, 'request'))

					success.append(chat)
					output['ok'] = True
				except Exception as e:
					output['fail'] = str(e)
					output['ok'] = False

			if( output['ok'] ):
				# message = self.convert_text(text, tz, 'save')
				# output['saved'] = self.query.insert([', '.join(success), output['message']['date'], message, output['message']['message_id'], bot_id], 'message')

				output['success'] = success
			else:
				output['ok'] = False
				output['status'] = 'Photo not sent'
		else:
			output['ok'] = False
			output['status'] = 'Bot not found'
		return output

	def get_messages(self, bot_id):
		return self.query.list({'bot_id': bot_id}, 'AND', 'message')

	def get_crons(self, bot_id, cron_id):
		if( cron_id == 'all' ):
			return self.query.list({'bot_id': bot_id}, 'AND', 'cron')
		else:
			return self.query.list({'bot_id': bot_id, 'id': cron_id}, 'AND', 'cron')

	def save_cron(self, bot_id, id, chats, text, date, tz, repeat, cron):
		output = {}
		if( id == '0' ):
			self.query.insert([chats, 1, date, repeat, text, tz, bot_id, cron], 'cron')
			output['cron'] = self.query.list({'bot_id': bot_id}, 'AND', 'cron')
			output['status'] = 'Saved'
			output['ok'] = True
			return output
		else:
			return [id, chats, text, date, repeat]
			# return self.query.update_cron(id, chats, text, date, repeat)

	def update_cron(self, bot_id, id, values):
		output = {}
		update = json.loads(values)
		self.query.update(update, 'cron', id)
		output['cron'] = self.query.list({'id': id}, 'AND', 'cron')
		output['ok'] = True
		return output

	def delete_cron(self, bot_id, id):
		output = {}
		output['ok'] = self.query.delete('cron', id)
		output['cron'] = self.query.list({'bot_id': bot_id}, 'AND', 'cron')
		return output

	def get_chats(self, bot_id):
		return self.query.list({'bot_id': bot_id}, 'AND', 'chats')

	def sign_in(self, name, email, hash):
		user = {}
		user['email'] = email
		output = {}
		if( len(self.query.list_users(user, 'OR')) == 0 ):
			self.query.add_user([name, email, hash])
			output['ok'] = True
			output['log_in'] = self.log_in(email, hash)
		else:
			output['ok'] = False
			output['status'] = 'exists'

		return output;

	def log_in(self, email, hash):
		output = {}
		
		inputs = {}
		inputs['email'] = email
		inputs['hash'] = hash

		user = self.query.list_users(inputs, 'AND')

		if( len(user) > 0 ):
			output['ok'] = True
			output['user'] = user
			output['bots'] = self.query.list({'user_id': user[0]['id']}, 'AND', 'bots')
		else:
			output['ok'] = False
			if( len(self.query.list_users({'email': email}, 'AND')) == 0 ):
				output['email'] = False
			if( len(self.query.list_users({'hash': hash}, 'AND')) == 0 ):
				output['hash'] = False

		return output

	def get_user(self, id):
		output = {}
		output['id'] = id

		user = self.query.list({'id': id}, 'AND', 'users')
		if( len(user) > 0 ):
			output['ok'] = True
			output['user'] = user
			output['bots'] = self.query.list({'user_id': id}, 'AND', 'bots')
		else:
			output['ok'] = False
			output['status'] = 'User not found'

		return output

	def get_me_bot(self, token):
		req = urllib2.Request( '{0}{1}/{2}'.format(self.telegram, token, 'getMe') )
		request = urllib2.urlopen(req)
		
		response = json.loads(request.read())

		return response

	def add_bot(self, user, token):
		getbot = self.get_me_bot(token)

		output = {}
		if( getbot['ok'] ):
			output['get_me'] = getbot
			# check bot in db
			local = self.query.list({'token': token, 'user_id': user}, 'AND', 'bots')
			if( len(local) > 0 ):
				output['ok'] = False
				output['status'] = 'You already have this bot'
			else:
				# save bot
				result = getbot['result']
				self.query.insert([token, result['username'], result['first_name'], str(result['id']), user], 'bots')
				output['bot'] = self.query.list({'token': token, 'user_id': user}, 'AND', 'bots')
				output['bots'] = self.query.list({'user_id': user}, 'AND', 'bots')
				output['ok'] = True
		else:
			output['ok'] = False
			output['status'] = 'Token Error'

		return output

	def add_channel(self, user_id, channel, bot_id):
		output = {}
		user = self.query.list({'id': user_id}, 'AND', 'users')

		if( len(user) > 0 ):
			if( len(self.query.list({'chat_id': channel, 'bot_id': bot_id}, 'AND', 'chats')) <= 0 ):
				self.query.insert([channel, channel, channel, bot_id], 'chats')
				output['ok'] = True
				output['chats'] = self.query.list({'bot_id': bot_id}, 'AND', 'chats')
			else:
				output['ok'] = False
				output['status'] = 'Channel is already present'

		return output

	def list_files(self, user_id):
		output = {}
		user = self.query.list({'id': user_id}, 'AND', 'users')

		if( len(user) > 0 ):
			folder = '{0}/files/{1}'.format(os.getcwd(), user[0]['name'])
			
			if( not os.path.isdir(folder) ):
				os.mkdir(folder)

			output['folders'] = os.listdir(folder)
			output['files'] = {}

			for drct in os.listdir(folder):
				for root, dirs, files in os.walk('{0}/{1}'.format(folder, drct)):
					output['files'][drct] = []
					
					for file in files:
						output['files'][drct].append(file)

					output['files'][drct].sort()

			output['ok'] = True
		else:
			output['ok'] = False
			output['status'] = 'User not found'

		return output

	def next_file(self, file, bot_id):
		file_obj = json.loads(file)
		folder = file_obj['folder']
		photo = file_obj['photo']

		bot = self.query.list({'id': bot_id}, 'AND', 'bots')
		user = self.query.list({'id': bot[0]['user_id']}, 'AND', 'users')

		if( len(user) > 0 ):
			files = self.list_files(user[0]['id'])

			if( len(files['files']) > 0 ):
				f_list = files['files'][folder]
				f_list.sort()

				index = f_list.index(photo)
				if( index == len(f_list)-1 ):
					index = -1

				file_obj['photo'] = f_list[index+1]
				file = json.dumps(file_obj)

		return file

	def query_close(self):
		self.query.db_close()
