# -*- coding: utf-8 -*-

import time
import json
import urllib2
from packages import xmltodict
from datetime import datetime as dt
from query import Query
from action import Action
from time import sleep

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Cron(object):

	def __init__(self, args):
		super(Cron, self).__init__()
		self.args = args
		self.query = Query(args);
		self.action = Action(args);

	def run(self):
		crons = self.query.list({}, 'AND', 'cron')
		output = []
		date = int(time.time())

		for action in crons:
			if( action['enable'] ):
				local = date - (action['tz_offset']*60*60)

				weekday = dt.utcfromtimestamp(local).weekday()
				hour = dt.utcfromtimestamp(local).hour
				minute = dt.utcfromtimestamp(local).minute

				dates = action['date'].split(',')

				for dte in dates:
					action_date = dt.utcfromtimestamp(int(dte) - (action['tz_offset']*60*60))
					cron_minute = action_date.minute
					cron_hour = action_date.hour

					if( action['repeat'] == 'hour' ):
						cron = {}

						# output.append({ str(action_date): (cron_minute < 30 and minute < 30) or (cron_minute > 29 and minute > 29) })

						if( (cron_minute < 30 and minute < 30) or (cron_minute > 29 and minute > 29) ):
							output.append(self.run_cron(action))
							cron['action'] = action

					if( action['repeat'] == 'day' ):
						cron = {}

						if( cron_hour == hour ):
							if( (cron_minute < 30 and minute < 30) or (cron_minute > 29 and minute > 29)  ):
								output.append(self.run_cron(action))
								cron['action'] = action

					if( action['repeat'] == 'week' ):
						cron = {}

						cron_weekday = action_date.weekday()

						if( weekday == cron_weekday and cron_hour == hour ):
							if( abs(cron_minute-minute) < 30 ):
								cron['message'] = self.action.send_message(action['bot_id'], action['chat_id'], action['text'], action['tz_offset'])
								cron['action'] = action

								output.append(cron)

		return output

	def run_cron(self, action):
		cron = {}
		if( len(action['cron']) > 0 and action['cron'] != 'null' ):
			# Cron contains photo or rss configuration
			cron_obj = json.loads(action['cron'])

			if 'photo' in cron_obj:
				cron['photo'] = self.action.send_photo(action['bot_id'], action['chat_id'], action['cron'], action['text'], action['tz_offset'])

				if( cron_obj['loop'] ):
					self.query.update({'cron': self.action.next_file(action['cron'], action['bot_id'])}, 'cron', action['id'])

			if 'rss' in cron_obj:
				rss_msg = self.complete_rss(cron_obj['resource'], cron_obj['rss'])
				if( len(rss_msg) > 0 ):
					cron['message'] = self.action.send_message(action['bot_id'], action['chat_id'], rss_msg, action['tz_offset'])
				else:
					cron['message'] = 'Failed to send rss'

			if 'weather' in cron_obj:
				weather = self.complete_weather(cron_obj['weather'])
				cron['weather'] = self.action.send_message(action['bot_id'], action['chat_id'], weather, action['tz_offset'])

		else:
			# Cron contains only text for message
			cron['message'] = self.action.send_message(action['bot_id'], action['chat_id'], action['text'], action['tz_offset'])

		return cron

	def complete_rss(self, resource, url):
		output = []

		if( resource == 'newsmaker.md' ):
			output.append('*{0}* - <DATE>'.format(resource))

			try:
				rss_url = urllib2.urlopen(url)
				data = rss_url.read()
				rss_url.close()

				rss = xmltodict.parse(data)

				text = []
				for k in rss['rss']['channel']['item']:
					# fields: title, link, guid, description, pubDate

					text.append('{0} [more..]({1})\n'.format(k['title'].decode('utf8'), k['link']))

				if( len(text) > 0 ):
					output.append('\n'.join(text))
				else:
					output = []

			except Exception as e:
				raise
			
		return '\n'.join(output)

	def complete_weather(self, city):
		output = []

		# Yandex city id - Chisinau - 33815
		try:
			y_url = urllib2.urlopen('http://export.yandex.ru/weather-ng/forecasts/33815.xml')
			data = y_url.read()
			y_url.close()

			rss = xmltodict.parse(data)

			# Debug
			# return rss['forecast']['day']

			text = []
			text.append('*{0}*'.format(rss['forecast']['@city']))

			for k in rss['forecast']:

				if 'fact' in k:
					fact = rss['forecast']['fact']
					text.append('t: *{0} C*'.format(fact['temperature']['#text']))
					text.append('humidity: *{0}*'.format(fact['humidity']))
					text.append('pressure: *{0}*'.format(fact['pressure']['#text']))

			if( len(text) > 0 ):
					output.append('\n'.join(text))
			else:
				output = []

		except Exception as e:
			raise

		return '\n'.join(output)

