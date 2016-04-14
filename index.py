import sys
import json
from py import global_var
from py import action
from py import cron

# f = open('log', 'a')

response = {}

# print json.dumps(sys.argv)

if( len(sys.argv) > 1 ):

	request = json.loads(sys.argv[1])
	
	if( request['action'] is not None ):
		name = request['action']

		action = action.Action(global_var)
		cron = cron.Cron(global_var)

		if( name == 'get_updates' ):
			response[name] = action.get_updates(request['bot_id'])

		if( name == 'get_messages' ):
			response[name] = action.get_messages(request['bot_id'])

		if( name == 'get_crons' ):
			response[name] = action.get_crons(request['bot_id'], request['cron_id'])

		if( name == 'get_chats' ):
			response[name] = action.get_chats(request['bot_id'])

		if( name == 'send_message' ):
			response[name] = action.send_message(request['bot_id'], request['chats_id'], request['text'].encode('utf-8'), request['tz'])

		if( name == 'send_photo' ):
			response[name] = action.send_photo(request['bot_id'], request['chats_id'], request['photo'], request['text'].encode('utf-8'), request['tz'])

		if( name == 'save_cron' ):
			response[name] = action.save_cron(request['bot_id'], request['cron_id'], request['chats_id'], request['text'].encode('utf-8'), request['date'], request['tz_offset'], request['repeat'], request['cron'])

		if( name == 'sign_in' ):
			response[name] = action.sign_in(request['name'], request['email'], request['hash'])

		if( name == 'log_in' ):
			response[name] = action.log_in(request['email'], request['hash'])

		if( name == 'add_bot' ):
			response[name] = action.add_bot(request['user_id'], request['token'])

		if( name == 'get_user' ):
			response[name] = action.get_user(request['id'])

		if( name == 'run_cron' ):
			response[name] = cron.run()

		if( name == 'update_cron' ):
			response[name] = action.update_cron(request['bot_id'], request['cron_id'], request['values'])

		if( name == 'delete_cron' ):
			response[name] = action.delete_cron(request['bot_id'], request['cron_id'])
		
		if ( name == 'list_files' ):
			response[name] = action.list_files(request['user_id'])

		if ( name == 'add_channel' ):
			response[name] = action.add_channel(request['user_id'], request['channel'], request['bot_id'])
	
	if( not response ):
		response['status'] = 'fail'

	print json.dumps(response)
else:
	response['status'] = 'fail'
	print json.dumps(response)

# f.close()