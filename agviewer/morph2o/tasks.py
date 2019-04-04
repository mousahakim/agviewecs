from __future__ import absolute_import, unicode_literals
from celery import shared_task
from visualizer.utils import *
from .decagon import *
# from visualizer.get_records import set_widget
# from visualizer.models import *
import xml.etree.ElementTree as ET
import time, json, requests, calendar
from datetime import datetime, timedelta
from django.db import IntegrityError
import smtplib

from memory_profiler import profile

@shared_task
def async_update():
	print 'creating async widget update tasks'
	from visualizer.models import Widgets
	widgets = Widgets.objects.all()

	if widgets.exists():
		for widget in widgets:
			if widget.widget_type == 'stat':
				update_stat_widget.delay(widget.widget_id)
			else:
				update_widget.delay(widget.widget, widget.user.username)

@shared_task
def update_stat_widget(widget_id):
	from visualizer.models import Widgets
	from visualizer.get_records import set_stat_widget
	from datetime import datetime
	try:
		widget = Widgets.objects.get(widget_id=widget_id)
	except Widgets.DoesNotExist as e:
		print e
		return

	dataset = widget.dataset.all()

	if dataset.exists():

		for data in dataset:

			duration = data.date_to - data.date_from
			data.date_from = datetime.now() - duration
			data.date_to = data.date_from + duration
			data.save()

			set_stat_widget(data.id)

@shared_task
def update_widget(widget, username):
	from visualizer.models import Widgets
	from visualizer.get_records import set_widget
	from django.contrib.auth.models import User
	try:
		user = User.objects.get(username=username)
	except User.DoesNotExist as e:
		print e
		return
	try:
		if widget['type'] == 'stat':
			new_widget = set_widget(widget, user)
			stat_widget = Widgets.objects.filter(widget_id=widget['id'], user=user)
			if stat_widget.exists():
				stat_widget.update(widget=new_widget)
			return
	except KeyError as e:
		print 'KeyError', e
		return

	from visualizer.utils import parse_date
	try:
		date_from = parse_date(widget['data']['range']['to'])
		date_to = parse_date(widget['data']['range']['from'])
	except KeyError as e:
		print 'KeyError', e
		return
	duration = date_from - date_to
	current_time = datetime.now()
	try:
		widget['data']['range']['from'] = date_to_string(current_time - duration)
		widget['data']['range']['to'] = date_to_string(current_time)
	except KeyError as e:
		print 'KeyError', e
		return

	new_widget = set_widget(widget, user)
	try:
		widget_in_db = Widgets.objects.filter(widget_id=widget['id'], user=user)
		if widget_in_db.exists():
			widget_in_db.update(widget=new_widget)
	except KeyError as e:
		print 'KeyError', e
		return
	new_widget = None
	monitor.delay(widget, username)


@shared_task
def async_alert(event_id):
	from visualizer.models import AlertEvents
	try:
		event = AlertEvents.objects.get(event_id=event_id)
	except AlertEvents.DoesNotExist as e:
		print e
		return
	
	if event.alert.email_alert and not event.sent:
		send_email(event_id)

	if event.alert.sms_alert and not event.sent:
		send_sms(event_id)

def send_sms(event_id):
	"""send email notification through
		email """
	from visualizer.models import AlertEvents, Widgets, SMSNotification
	from twilio.rest import Client
	try:
		event = AlertEvents.objects.get(event_id=event_id)
	except AlertEvents.DoesNotExist as e:
		print e
		return

	try:
		appuser = AppUser.objects.get(user=event.user)
	except AppUser.DoesNotExist as e:
		print e
		return

	if appuser.phone_number is None or appuser.phone_number == '':
		return

	try:
		widget = Widgets.objects.get(widget_id=event.widget)
		widget_title = widget.widget['title']
	except Widgets.DoesNotExist as e:
		print e
		widget_title = 'Non-existing widget'

	user = event.user

	# Your Account SID from twilio.com/console
	account_sid = "AC56569f940dd4ccecc02dbe962c8bb3d5"
	# Your Auth Token from twilio.com/console
	auth_token  = "16eae7d78b988fc3af05cf2be40e76f7"

	client = Client(account_sid, auth_token)

	from_ = "+56997134785"
	to = appuser.phone_number

	# subject = 'AgViewer: ' + event.alert.name + ' '+ event.alert.type.upper()
	message = widget_title + '\t'+ event.alert.type.upper() +'\n'+ event.alert.name +'\t'+date_to_string(event.t_notify)\
	+ '\n' + event.alert.message + '\t' + event.value

	# message = """From: %s\nTo: %s\nSubject: %s\n\n%s
	# """ % (from_, ", ".join(to), subject, body)

	sms = client.messages.create(to=to, from_=from_, body=message)

	try:
		sms_noti = SMSNotification(user=user, subject=alert.alert.name, content=message, success=True, error=sms.sid)
		sms_noti.save()
		event.sent = True
		event.save()
	except ValueError as e:
		print e
		print 'failed to save sms notification'	


def send_email(event_id):
	"""send email notification through
		email """
	from visualizer.models import AlertEvents, SMTPConfig, Widgets, EmailNotification, SMSNotification
	try:
		event = AlertEvents.objects.get(event_id=event_id)
	except AlertEvents.DoesNotExist as e:
		print e
		return

	try:
		appuser = AppUser.objects.get(user=event.user)
	except AppUser.DoesNotExist as e:
		print e
		return

	if appuser.email_add is None or appuser.email_add == '':
		return

	try:
		configs = SMTPConfig.objects.get(use_this=True)
	except SMTPConfig.DoesNotExist as e:
		print e
		return

	try:
		widget = Widgets.objects.get(widget_id=event.widget)
		widget_title = widget.widget['title']
	except Widgets.DoesNotExist as e:
		print e
		widget_title = 'Non-existing widget'

	user = event.user

	# if not self.has_email(user):
	# 	print 'no email address provided'
	# 	return

	from_ = configs.username
	to = appuser.email_add.split(',')

	subject = 'AgViewer ' +event.alert.type.upper()+ ': ' + event.alert.name
	body = event.station + '\t\t' + widget_title + '\t\t' + date_to_string(event.t_notify) + '\n\n' + event.alert.message + '\t\t' + event.value

	message = """From: %s\nTo: %s\nSubject: %s\n\n%s
	""" % (from_, ", ".join(to), subject, body)

	print from_
	print to
	print message

	try:
		if configs.tls:
			server = smtplib.SMTP(configs.server_address, configs.port)
			if configs.esmtp:
				server.ehlo()
			else:
				server.helo()
			server.starttls()
			server.login(configs.username, configs.password)
			server.sendmail(from_, to, message)
			server.close()
			print 'email sent successfully.'
			try:
				email_noti = EmailNotification(user=user, subject=subject, content=body, success=True)
				email_noti.save()
			except:
				print 'failed to save email notification'
		elif configs.ssl:
			server = smtplib.SMTP_SSL(configs.server_address, configs.port)
			if configs.esmtp:
				server.ehlo()
			else:
				server.helo()
			server.login(configs.username, configs.password)
			# server.starttls()
			# if configs.esmtp:
			# 	server.ehlo()
			# else:
			# 	server.helo()
			server.sendmail(from_, to, message)
			server.close()
			event.sent = True
			event.save()
			print 'email sent successfully.'
			try:
				email_noti = EmailNotification(user=user, subject=subject, content=body, success=True, error='email sent successfully')
				email_noti.save()
			except ValueError as e:
				print e
				print 'failed to save email notification'
	except smtplib.SMTPException as e:
		print e
		print 'failed to send email.'
		try:
			email_noti = EmailNotification(user=user, subject=subject, content=body, success=False, error='failed to send email')
			email_noti.save()
		except:
			print 'failed to save email notification'
	

@shared_task
def async_download():
	print 'creating async download tasks'
	from visualizer.models import Stations
	dg_stations = list(set([st.station for st in Stations.objects.filter(database='dg')]))
	fc_stations = list(set([st.station for st in Stations.objects.filter(database='fc')]))

	if dg_stations != []:
		for station in dg_stations:
			download.delay(station=station, db='dg')

	if fc_stations != []:
		for station in fc_stations:
			download.delay(station=station, db='fc')

	print '%d tasks created.' % (len(dg_stations)+len(fc_stations))

@shared_task
def download(station=None, db=None):
	
	if station != None and db != None:
		print 'Download started. ', datetime.now()
		if db == 'fc':
			get_data_fc(station)
			get_model_data_fc(station)
			update_sensor_lst(station)
			return
		elif db == 'dg':
			get_data_dg(station)
			return
		else:
			return
        from visualizer.models import Stations
	print 'Periodic download started. ', datetime.now()
	dg_stations = list(set([st.station for st in Stations.objects.filter(database='dg')]))
	fc_stations = list(set([st.station for st in Stations.objects.filter(database='fc')]))

	#get dg data
	if dg_stations != []:
		for station in dg_stations:
			get_data_dg(station)

	# get fc data
	if fc_stations != []:
		for station in fc_stations:
			get_data_fc(station)
			get_model_data_fc(station)
			update_sensor_lst(station)

def update_sensor_lst(station_id):
	from visualizer.models import Stations

	stations = Stations.objects.filter(station=station_id)
	if not stations.exists():
		print 'no station. exiting...'
		return

	sensors = stations[0].sensors
	# un-comment to get sensor list throuh station/sensors route
	# and not data
	# sensor_lst = get_sensor_lst(station_id)
	path = '/data/'+station_id+'/hourly/last/1'
	headers = make_headers('GET', path)
	try:
		response = requests.get('https://api.fieldclimate.com' + path, headers=headers, verify=False)
	except response.exceptions.RequestException as e:
		print e
		return

	try:
		sensor_lst = json.loads(response.text)['sensors']
	except KeyError as e:
		print e
		return
	try:
		data = json.loads(response.text)['data'][0]
	except IndexError as e:
		print 'No data retrieved', e
		return

	if sensor_lst is None:
		print 'failed to get sensor list. exiting...'
		return
	for sensor in sensor_lst:
		for val in sensor['aggr']:
			if sensor['aggr'][val] != 1:
				continue 
			sensor_name = ''
			try:
				sensor_code = str(sensor['ch']) +'_'+ sensor['mac'] +'_'+ sensor['serial'] +'_'+ str(sensor['code']) +'_'+ val #
				if sensor['name_custom'] is None:
					sensor_name = sensor['name'] +' ['+ str(sensor['ch']) +' '+ val + ']'
				else:
					sensor_name = sensor['name_custom'] +' ['+ str(sensor['ch']) +' '+ val + ']'
				if sensor_code in data:
					sensors.update({sensor_code:sensor_name})
			except KeyError as e:
				pass
				# print 'KeyError', e
	# for k, v in sensors.iteritems():
	# 	print k, v
	stations.update(sensors=sensors)

	return sensors

def get_data_dg(device):
	from visualizer.models import Stations, AppUser, StationData
	print 'downloading decagon data...'
	mrid = 0
	mydevice = Stations.objects.filter(station=device)
	if not mydevice.exists():
		return False
	prev_records = StationData.objects.filter(station_id=device)
	if prev_records.exists():
		print 'Some data exists'
		mrid = prev_records.last().mrid
	try:
		dg_acc = AppUser.objects.get(user=mydevice[0].user)
		params = {
			'email': dg_acc.dg_username,
			'userpass': dg_acc.dg_password,
			'deviceid': device,
			'devicepass': mydevice[0].code,
			'report': 1,
			'mrid': mrid,
			'User-Agent': 'AgViewer_1.0'
		}
		url = 'http://api.ech2odata.com/morph2ola/dxd.cgi'
		response = requests.post(url, data=params)
		if response.status_code == 200:
			data = parse_dxd(response.text)
			if data is None:
				return False		
			for item in data:
				if parse_date_s(json.loads(item)['date']).year > datetime.now().year:
					continue
				try:
					record = StationData(station_id=device, database='dg', mrid=get_rid(response.text), date=parse_date_s(json.loads(item)['date']), data=json.loads(item))
					record.save()
				except IntegrityError as e:
					continue
	except requests.exceptions.RequestException as e:
		# print e
		pass
	
	
	return True

# @profile
def get_data_fc(station,min_date=None, max_date=None):
	from visualizer.models import Stations, AppUser, StationData
	from django.contrib.auth.models import User
	MAX_RETRIES = 3
	try:
		user = AppUser.objects.get(user=User.objects.get(username='admin')) # this isn't needed!!
	except (User.DoesNotExist, AppUser.DoesNotExist) as e:
		print e, 'user does not exist.'
		return

	dt_from = ''
	prev_records = StationData.objects.filter(station_id=station)
	if prev_records.exists():
		dt_from = calendar.timegm(prev_records.last().date.timetuple())
	else:
		minmax_date = get_minmax(station)
		if minmax_date is not None:
			if parse_date(minmax_date['max_date']) - parse_date(minmax_date['min_date']) > timedelta(weeks=48):
				dt_from = parse_date(minmax_date['max_date']) - timedelta(weeks=47)
			else:
				dt_from = parse_date(minmax_date['min_date'])
			print 'downloading data since: ', dt_from
			dt_from = calendar.timegm(dt_from.timetuple())
		else:
			print 'cannot retrieve min/max data available.'
			print 'requesting data 44 weeks from now.'
			dt_from = calendar.timegm((datetime.now() - timedelta(weeks=44)).timetuple())

	if min_date is not None:
		dt_from = calendar.timegm(min_date.timetuple())

	if max_date is not None:
		dt_to = calendar.timegm(max_date.timetuple())
		path = '/data/'+station+'/raw/from/'+str(dt_from)+'/to/'+str(dt_to)
	else:
		path = '/data/'+station+'/raw/from/'+str(dt_from)	
	# test
	
	# dt_to = calendar.timegm((prev_records.last().date + timedelta(hours=2)).timetuple())
	# path = '/data/'+station+'/hourly/from/'+str(dt_from)+'/to/'+str(dt_to)

	# end test code
	# path = '/data/'+station+'/hourly/from/'+str(dt_from)
	headers = make_headers('GET', path)
	url = 'https://stage.fieldclimate.com'
	response = None
	while MAX_RETRIES > 1:
		MAX_RETRIES -= 1
		try:
			# verify=false: this needs to be fixed
			response = requests.get(url + path, headers=headers, verify=False) 
		except requests.exceptions.RequestException as e:
			print e 
			print 'Retrying in a seconds...'
			time.sleep(1)
			continue
		if response.status_code != 200:
			print 'Server returned http ', response.status_code
			print 'Retrying in a seconds...'
			time.sleep(1)
			continue
		else:
			print 'Server returned http ', response.status_code
			break
		response = None

	# if max retries exceeded before getting a 200 response return None 
	if response.status_code != 200: 
		return True
		
	data = json.loads(response.text)

	try:
		for record in data['data']:
			if parse_date(record['date']).year > datetime.now().year:
				continue
			try:
				new_record = StationData(station_id=station, database='fc', mrid=0, date=parse_date_s(record['date']).replace(second=0), data=record)
				new_record.save()
			except IntegrityError as e:
				print 'IntegrityError', e
				continue
	except KeyError as e:
		# print 'KeyError', e
		pass

	#check for disease model data and store if any exists
	#also update station's sensor list if required
	station_obj = Stations.objects.filter(station=station)
	if not station_obj.exists():
		return True
	sensors = station_obj[0].sensors
	if 'extra' in data:
		print 'disease model data exists'
		try:
			for key, val in data['extra']['model'][station].iteritems():
				record = StationData.objects.filter(station_id=station, database='fc', date=parse_date_s(key).replace(second=0))
				if record.exists():
					new_data = record[0].data
					for d_model, value in val.iteritems():
						new_data.update({d_model:value})
						record.update(data=new_data)
						#also update list of sensors
						if d_model not in sensors:
							print 'sensor list updated', d_model
							sensors.update({d_model:d_model})
							station_obj.update(sensors=sensors)
				else:
					# this probably never happens
					print 'No corresponding record exists. disease model data cannot be saved'
		except KeyError as e:
			# print 'KeyError', e
			pass

	#try to retrieve model data not returned along with raw data
	model_data = StationData.objects.filter(station_id=station).reverse()
	if not model_data.exists():
		return True
	# for record in model_data:
	# 	if record

	return True

def get_model_data_fc(station):
	from visualizer.models import Stations, StationData

	#check the latest diseas model data available
	model_data = StationData.objects.filter(station_id=station).reverse()
	dt_from = ''
	if not model_data.exists():
		return
	for record in model_data:
		#this is not good but the only way for now
		if record.data.has_key('ETo[mm]'):
			# print record.date
			dt_from = calendar.timegm(record.date.timetuple())
			break
	print 'last model data', dt_from
	view = {
		'name': 'eto',
		'data': {
			'model': 'Evapotranspiration'
		}
	}
	path = '/data/'+station+'/daily/from/'+str(dt_from)
	headers = make_headers('POST', path)
	url = 'https://api.fieldclimate.com'

	try:
		response = requests.post(url + path, headers=headers, data=view, verify=False)
	except requests.exceptions.RequestException as e:
		#will not retry because it is retried every hour anyway
		print e
		return

	if response.status_code != 200:
		print response.text
		return
	model_data = json.loads(response.text)

	#check for disease model data and store if any exists
	#also update station's sensor list if required
	station_obj = Stations.objects.filter(station=station)
	sensors = station_obj[0].sensors
	if 'extra' in model_data:
		print 'disease model data exists'
		try:
			for key, val in model_data['extra']['model'][station].iteritems():
				record = StationData.objects.filter(station_id=station, database='fc', date=parse_date_s(key).replace(second=0))
				print key
				if record.exists():
					new_data = record[0].data
					for d_model, value in val.iteritems():
						new_data.update({d_model:value})
						record.update(data=new_data)
						# print 'record updated', new_data
						#update list of sensors
						if d_model not in sensors:
							# print 'sensor list updated', d_model
							sensors.update({d_model:d_model})
							station_obj.update(sensors=sensors)
				else:
					# this probably never happens
					print 'No corresponding record exists. disease model data cannot be saved'
		except KeyError as e:
			# print 'KeyError', e
			pass

def parse_dxd(dxd):
	
	root = ET.fromstring(dxd)
	data_list = []
	sensors = {}
	raw_string = None
	for element in root.iter('Device'):
		station_id = element.attrib['id']
		station_name = element.attrib['name']
	for element in root.iter('Data'):
		raw_string = element.text

	if raw_string is None:
		return None 

	data_lines = raw_string.replace('\t','').splitlines()
	data_lines.pop(0)
	for line in data_lines:
		dic = {'date':decatime(line.split(',')[0])}
		i = 1
		j = 1
		for element in root.iter('Port'):
			if element.attrib['value'] in dic:
				dic.update({element.attrib['value']+'-'+element.attrib['number']: float(line.split(',')[i])})
				j += 1
			else:
				dic.update({element.attrib['value']+'-'+element.attrib['number']: float(line.split(',')[i])})
			i +=1
		data_list.extend([json.dumps(dic, sort_keys=True)])
	return data_list

def get_rid(dxd):
	root = ET.fromstring(dxd)
	for element in root.iter('Data'):
		mrid = int(element.attrib['rid'])
		return mrid

@shared_task
def monitor(widget, username):
	from django.contrib.auth.models import User
	from visualizer.general import Alert
	import datetime
	
	if widget['type'] == 'stat':
		if w_calc != 'rain_accumulation_24h':
			return	
		w_calc = widget['data']['calc']['params']['data']
		w_station = widget['data']['calc']['params']['station_id']
		w_db = widget['data']['calc']['params']['db']
		w_sensor = widget['data']['calc']['params']['sensor']
		#sensor id in complete format
		w_sensor_id = w_db+'-'+w_station+'-'+w_sensor
		w_value = widget['data']['calc']['value']

		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist as e:
			print e
			return

		alerts = Alert.has_alerts(user, w_sensor_id, None)
		w_date = datetime.datetime.now()
		if w_date is None:
			return
		for a in alerts:
			event = {
				'value': w_value if w_value is not None else 0,
				'date': d['date'],
				'widget_id': widget['id'],
				'sensor': [w_sensor_id]
			}
			alert = Alert.alert_from_model_obj(a)
			alert.watch(event, None, 'accum_precipitation')

	elif widget['type'] == 'main-chart':
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist as e:
			print e
			return

		if widget['data']['raw_sensors'] is not None:
			w_values = widget['data']['raw_sensors']['value']

			for values in w_values:
				sensor = values[0]['label_id']
				db = ''
				try:
					db = sensor.split('-')[0]
				except KeyError as e:
					print e
					return
				extract = None
				if db == 'dg':
					extract = values[0]['axis_id']
				alerts = Alert.has_alerts(user, sensor, None)

				for v in values:
					#do not evaluate null value
					if v['value'] is None:
						continue
					for a in alerts:
						event = {
							'value': v['value'],
							'date': v['date'],
							'widget_id': widget['id'],
							'sensor': [sensor],
							'extract': extract,
						}
						alert = Alert.alert_from_model_obj(a)
						# print alert.alert_dict
						if db == 'dg':
							if extract is not None and alert.alert_dict['extract'] is not None and extract != alert.alert_dict['extract']:
								continue
						alert.watch(event, sensor, None)


		if widget['data']['paw'] is not None:
			w_sensors = widget['data']['paw']['params']['sensors']
			w_paw_avg = widget['data']['paw']['params']['avg']
			w_values = widget['data']['paw']['value']

			for values in w_values:
				sensor = values[0]['sensor'] if not w_paw_avg else None
				alerts = Alert.has_alerts(user, None, 'paw')

				for v in values:
					#do not evaluate null value
					if v['value'] is None:
						continue
					for a in alerts:
						event = {
							'value': v['value'],
							'date': v['date'],
							'widget_id': widget['id'],
							'sensor': [sensor] if not w_paw_avg else w_sensors
						}
						alert = Alert.alert_from_model_obj(a)
						alert.watch(event, None, 'paw')

		if widget['data']['chilling_portions'] is not None:
			w_sensor = widget['data']['chilling_portions']['params']['sensors']
			w_values = widget['data']['chilling_portions']['value']
			alerts = Alert.has_alerts(user, None, 'chilling_portions')

			for v in w_values:
				#do not evaluate null value
				if v['value'] is None:
					continue
				for a in alerts:
					event = {
						'value': v['value'],
						'date': v['date'],
						'widget_id': widget['id'],
						'sensor': [w_sensor]
					}
					alert = Alert.alert_from_model_obj(a)
					alert.watch(event, None, 'chilling_portions')

		if widget['data']['degree_days'] is not None:
			w_sensor = widget['data']['degree_days']['params']['sensors']
			w_values = widget['data']['degree_days']['value']
			alerts = Alert.has_alerts(user, None, 'degree_days')

			for v in w_values:
				#do not evaluate null value
				if v['value'] is None:
					continue
				for a in alerts:
					event = {
						'value': v['value'],
						'date': v['date'],
						'widget_id': widget['id'],
						'sensor': [w_sensor]
					}
					alert = Alert.alert_from_model_obj(a)
					alert.watch(event, None, 'degree_days')

		if widget['data']['chilling_hours'] is not None:
			w_sensor = widget['data']['chilling_hours']['params']['sensors']
			w_values = widget['data']['chilling_hours']['value']
			alerts = Alert.has_alerts(user, None, 'chilling_hours')

			for v in w_values:
				#do not evaluate null value
				if v['value'] is None:
					continue
				for a in alerts:
					event = {
						'value': v['value'],
						'date': v['date'],
						'widget_id': widget['id'],
						'sensor': [w_sensor]
					}
					alert = Alert.alert_from_model_obj(a)
					alert.watch(event, None, 'chilling_hours')

		if widget['data']['evapo'] is not None:
			w_sensor_temp = widget['data']['evapo']['params']['temp']
			w_sensor_rh = widget['data']['evapo']['params']['rh']
			w_sensor_sr = widget['data']['evapo']['params']['sr']
			w_sensor_ws = widget['data']['evapo']['params']['ws']
			w_sensors = [w_sensor_temp, w_sensor_rh, w_sensor_sr, w_sensor_ws]
			w_values = widget['data']['evapo']['value']
			alerts = Alert.has_alerts(user, None, 'evapo')

			for v in w_values:
				#do not evaluate null value
				if v['value'] is None:
					continue
				for a in alerts:
					event = {
						'value': v['value'],
						'date': v['date'],
						'widget_id': widget['id'],
						'sensor': w_sensors
					}
					alert = Alert.alert_from_model_obj(a)
					alert.watch(event, None, 'evapo')

		if widget['data']['dew_point'] is not None:
			# print 'monitoring dew point widget'
			w_sensor_temp = widget['data']['dew_point']['params']['temp']
			w_sensor_rh = widget['data']['dew_point']['params']['rh']
			w_sensors = [w_sensor_temp, w_sensor_rh]
			w_values = widget['data']['dew_point']['value']
			alerts = Alert.has_alerts(user, None, 'dew_point')

			for v in w_values:
				#do not evaluate null value
				if v['value'] is None:
					continue
				for a in alerts:
					event = {
						'value': v['value'],
						'date': v['date'],
						'widget_id': widget['id'],
						'sensor': w_sensors
					}
					alert = Alert.alert_from_model_obj(a)
					alert.watch(event, None, 'dew_point')

		if widget['data']['ex_ec'] is not None:
			w_all_sensors = {}
			w_values = widget['data']['ex_ec']['value']
			alerts = Alert.has_alerts(user, None, 'ex_ec')
			for sensor in widget['data']['ex_ec']['params']['sensors']:
				# sensor['label'] maynot be unique in which case this needs to be fixed
				w_all_sensors.update({sensor['label']:sensor['sensors']})

			for values in w_values:
				try:
					graph_sensors = w_all_sensors[values[0]['label']]
				except KeyError as e:
					print e
					graph_sensors = []
				
				for v in values:
					#do not evaluate null value
					if v['value'] is None:
						continue
					for a in alerts:
						event = {
							'value': v['value'],
							'date': v['date'],
							'widget_id': widget['id'],
							'sensor': graph_sensors
						}
						alert = Alert.alert_from_model_obj(a)
						alert.watch(event, None, 'ex_ec')
































