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


@shared_task
def async_update():
	print 'creating async widget update tasks'
	from visualizer.models import Widgets
	widgets = Widgets.objects.all()

	if widgets.exists():
		for widget in widgets:
			update_widget.delay(widget.widget, widget.user.username)


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


@shared_task
def async_alert(user):
	pass

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
			update_sensor_lst(station)

# def update_sensor_lst(station_id):
# 	from visualizer.models import Stations, StationData, SensorCodes

# 	stations = Stations.objects.filter(station=station_id)
# 	if not stations.exists():
# 		return
# 	sensors = stations[0].sensors
# 	data = StationData.objects.filter(station_id=station_id)
# 	if not data.exists():
# 		return

# 	for key, val in data.last().data.iteritems(): # look for new sensor
# 		if key not in ['f_log_int', 'f_date'] and\
# 		key not in stations[0].inactive_sensors and\
# 		key not in sensors:
# 			sensor_code = key.split('_')[-1]
# 			if SensorCodes.objects.filter(sensor_id=sensor_code).exists():
# 				sensors.update({key:SensorCodes.objects.filter(sensor_id=sensor_code)[0].sensor_name})
# 			else:
# 				sensors.update({key:key})

# 	last_record_dt = data.last().date
# 	data_36h = data.filter(date__range=(last_record_dt - timedelta(hours=36), last_record_dt ))
# 	active_sensors = {}
# 	inactive_sensors = {}
# 	for rec in data_36h:
# 		for key, val in rec.data.iteritems():
# 			try:
# 				if rec.data[key] is not None:
# 					active_sensors.update({key:val})
# 			except KeyError as e:
# 				print e

# 	for key, val in data.last().data.iteritems():
# 		if key not in ['f_log_int', 'f_date'] and key not in active_sensors:
# 			inactive_sensors.update({key:val})

# 	stations.update(sensors=active_sensors, inactive_sensors=inactive_sensors)

# def update_sensor_lst(station_id):
# 	from visualizer.models import Stations, StationData, SensorCodes

# 	stations = Stations.objects.filter(station=station_id)
# 	if not stations.exists():
# 		print 'no station. exiting...'
# 		return
# 	data = StationData.objects.filter(station_id=station_id)
# 	if not data.exists():
# 		print 'no data. exiting...'
# 		return
# 	sensors = {}
# 	sensor_lst = get_sensor_lst(station_id)
# 	if sensor_lst is None:
# 		print 'failed to get sensor list. exiting...'
# 		return
# 	for sensor in sensor_lst: # build dict of sensors 
# 		no_postfix = True

# 		if SensorCodes.objects.filter(sensor_id=sensor['f_sensor_code']).exists():
# 			sensor_user_name = SensorCodes.objects.filter(sensor_id=sensor['f_sensor_code'])[0].sensor_name
# 		else:
# 			sensor_user_name = 'no name'

# 		if sensor['f_val_aver'] == '1': 
# 			sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+' aver]'
# 			key = 'sens_aver_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 			sensors.update({key:sensor_name})
# 			no_postfix = False
# 		if sensor['f_val_min'] == '1': 
# 			sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+' min]'
# 			key = 'sens_min_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 			sensors.update({key:sensor_name})
# 			no_postfix = False
# 		if sensor['f_val_max'] == '1': 
# 			sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+' max]'
# 			key = 'sens_max_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 			sensors.update({key:sensor_name})
# 			no_postfix = False
# 		if sensor['f_val_last'] == '1': 
# 			sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+']'
# 			key = 'sens_last_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 			sensors.update({key:sensor_name})
# 			no_postfix = False
# 		if sensor['f_val_sum'] == '1': 
# 			sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+']'
# 			key = 'sens_sum_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 			sensors.update({key:sensor_name})
# 			no_postfix = False
# 		# if sensor['f_val_neg'] == '1': 
# 		# 	sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+']'
# 		# 	key = 'sens_neg_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 		# 	sensors.update({key:sensor_name})
# 		# 	no_postfix = False
# 		# if sensor['f_val_log'] == '1': 
# 		# 	sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+']'
# 		# 	key = 'sens_log_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 		# 	sensors.update({key:sensor_name})
# 		# 	no_postfix = False
# 		# if sensor['f_val_user'] == '1': 
# 		# 	sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+']'
# 		# 	key = 'sens_user_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 		# 	sensors.update({key:sensor_name})
# 		# 	no_postfix = False
# 		# if sensor['f_val_axilary'] == '1': 
# 		# 	sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+']'
# 		# 	key = 'sens_axilary_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 		# 	sensors.update({key:sensor_name})
# 		# 	no_postfix = False
# 		if no_postfix:
# 			key = 'sens_'+sensor['f_sensor_ch']+'_'+sensor['f_sensor_code']
# 			sensor_name = sensor_user_name + '[ '+sensor['f_sensor_ch']+']'
# 		sensors.update({key:sensor_name})

# 	last_record_dt = data.last().date
# 	data_72h = data.filter(date__range=(last_record_dt - timedelta(hours=120), last_record_dt ))
# 	active_sensors = {}
# 	for rec in data_72h: # if no data for 72 hours leave sensor in inactive list.
# 		for key, val in sensors.items():
# 			try:
# 				if rec.data[key] is not None:
# 					active_sensors.update({key:val})
# 					del sensors[key]
# 			except KeyError as e:
# 				print e

# 	stations.update(sensors=active_sensors, inactive_sensors=sensors)

def update_sensor_lst(station_id):
	from visualizer.models import Stations

	stations = Stations.objects.filter(station=station_id)
	if not stations.exists():
		print 'no station. exiting...'
		return

	sensors = stations[0].sensors
	sensor_lst = get_sensor_lst(station_id)
	if sensor_lst is None:
		print 'failed to get sensor list. exiting...'
		return
	for sensor in sensor_lst:
		for val in sensor['aggr']:
			sensor_name = ''
			try:
				sensor_code = str(sensor['ch']) +'_'+ sensor['mac'] +'_'+ sensor['serial'] +'_'+ str(sensor['code']) +'_'+ val #
				if sensor['name_custom'] is None:
					sensor_name = sensor['name'] +' ['+ str(sensor['ch']) +' '+ val + ']'
				else:
					sensor_name = sensor['name_custom'] +' ['+ str(sensor['ch']) +' '+ val + ']'
				sensors.update({sensor_code:sensor_name})
			except KeyError as e:
				print 'KeyError', e
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
				try:
					record = StationData(station_id=device, database='dg', mrid=get_rid(response.text), date=parse_date_s(json.loads(item)['date']), data=json.loads(item))
					record.save()
				except IntegrityError as e:
					continue
	except requests.exceptions.RequestException as e:
		print e
	
	
	return True


# def get_data_fc(station, st_user=None):
# 	from visualizer.models import Stations, AppUser, StationData
# 	user = st_user
# 	if st_user is None:
# 		user = Stations.objects.filter(station=station)[0].user

# 	dt_from = parse_date_s('2016-01-01 12:00:00')
# 	prev_records = StationData.objects.filter(station_id=station)
# 	if prev_records.exists():
# 		dt_from = prev_records.last().date

# 	minmax_date = get_minmax(user, 'fc', station)
# 	max_entry = parse_date_s(minmax_date['f_date_max'])

# 	row_count = get_row_count(user, 'fc', station, dt_from, max_entry)

# 	try:
# 		fc_acc = AppUser.objects.get(user=user)
# 		response = requests.post("http://fieldclimate.com/api/index.php?action=CIDIStationData_GetFromDate",
# 			data={
# 				"user_name": fc_acc.fc_username,
# 			 	"user_passw" : fc_acc.fc_password,
# 			 	"station_name": station,
# 			 	"dt_from": dt_from,
# 			 	"row_count": row_count,
# 			 	"group_code": 1
# 			 	})
# 		response = None
# 		response = requests.post("http://fieldclimate.com/api/index.php?action=CIDIStationData_GetFromDate",
# 			data={
# 				"user_name": fc_acc.fc_username,
# 			 	"user_passw" : fc_acc.fc_password,
# 			 	"station_name": station,
# 			 	"dt_from": dt_from,
# 			 	"row_count": row_count,
# 			 	"group_code": 1
# 			 	})
# 	except requests.exceptions.RequestException as e:
# 		print e

# 	if is_json(response.text):
# 		if json.loads(response.text).has_key('ReturnDataSet'):
# 			for i, v in enumerate(json.loads(response.text)['ReturnDataSet']):
# 				try:
# 					record = StationData(station_id=station, database='fc', mrid=0, date=parse_date_s(v['f_date']), data=v)
# 					record.save()
# 				except IntegrityError as e:
# 					continue
# 			return True
# 	return False

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
			dt_from = calendar.timegm(parse_date(minmax_date['min_date']).timetuple())
		else:
			print 'cannot retrieve min/max data available.'
			return
	if min_date is not None:
		dt_from = calendar.timegm(min_date.timetuple())
	if max_date is not None:
		dt_to = calendar.timegm(max_date.timetuple())
		path = '/data/'+station+'/hourly/from/'+str(dt_from)+'/to/'+str(dt_to)
	else:
		path = '/data/'+station+'/hourly/from/'+str(dt_from)	
	# test
	
	# dt_to = calendar.timegm((prev_records.last().date + timedelta(hours=2)).timetuple())
	# path = '/data/'+station+'/hourly/from/'+str(dt_from)+'/to/'+str(dt_to)

	# end test code
	path = '/data/'+station+'/hourly/from/'+str(dt_from)
	headers = make_headers('GET', path)
	url = 'https://api.fieldclimate.com'
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
	if response is None: 
		return

	data = json.loads(response.text)

	try:
		for record in data['data']:
			try:
				new_record = StationData(station_id=station, database='fc', mrid=0, date=parse_date_s(record['date']), data=record)
				new_record.save()
			except IntegrityError as e:
				print 'IntegrityError', e
				continue
	except KeyError as e:
		print 'KeyError', e

	#check for disease model data and store if any exists
	#also update station's sensor list if required
	station_obj = Stations.objects.filter(station=station)
	sensors = station_obj[0].sensors
	if 'extra' in data:
		print 'disease model data exists'
		try:
			for key, val in data['extra']['model'][station].iteritems():
				record = StationData.objects.filter(station_id=station, database='fc', date=parse_date_s(key))
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
			print 'KeyError', e

	#try to retrieve model data not returned along with raw data
	model_data = StationData.objects.filter(station_id=station).reverse()
	if not model_data.exists():
		return
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
			print record.date
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
				record = StationData.objects.filter(station_id=station, database='fc', date=parse_date_s(key))
				if record.exists():
					new_data = record[0].data
					for d_model, value in val.iteritems():
						new_data.update({d_model:value})
						record.update(data=new_data)
						print 'record updated', new_data
						#update list of sensors
						if d_model not in sensors:
							print 'sensor list updated', d_model
							sensors.update({d_model:d_model})
							station_obj.update(sensors=sensors)
				else:
					# this probably never happens
					print 'No corresponding record exists. disease model data cannot be saved'
		except KeyError as e:
			print 'KeyError', e








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




def update_widgets(widgets):
	from visualizer.models import Widgets
	print 'updating widgets ...'
	for widget in widgets:
		old_widget = widget.widget
		if widget.widget_type == 'stat':
			
			db = old_widget['data']['calc']['params']['db']
			if db == 'dg':
				print 'decagon sensor skipped.'
				continue
			station = old_widget['data']['calc']['params']['station_id']
			sub_sensor_parts = old_widget['data']['calc']['params']['sensor'].split('_')
			channel = sub_sensor_parts[-2]
			code = sub_sensor_parts[-1]
			aggr = sub_sensor_parts[1]
			new_sensor_code = convert_sensor(station, channel, code, aggr, 'stat')
			old_widget['data']['calc']['params']['sensor'] = new_sensor_code
			Widgets.objects.filter(widget_id=widget.widget_id, user=widget.user).update(widget=old_widget)
			continue

		for key, val in old_widget['data'].items():
			if key not in ['title', 'range', 'calc']:
				if val is not None:
					try:
						if key == 'ex_ec':
							for i, v in enumerate(val['params']['sensors']):
								if v is None:
									continue
								for iterator, value in enumerate(v['sensors']):
									sensor_parts = value.split('-')
									db = sensor_parts[0]
									if db == 'dg':
										print 'decagon sensor skipped.'
										continue
									station = sensor_parts[1]
									sensor = sensor_parts[2]
									sub_sensor_parts = sensor.split('_')
									channel = sub_sensor_parts[-2]
									code = sub_sensor_parts[-1]
									aggr = sub_sensor_parts[1]
									new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
									val['params']['sensors'][i]['sensors'][iterator] = new_sensor_code
						elif key == 'paw':
							print 'processing ', key
							for i, v in val['params']['pawFields'].items():
								sensor_parts = i.split('-')
								db = sensor_parts[0]
								if db == 'dg':
									print 'decagon sensor skipped.'
									continue
								station = sensor_parts[1]
								sensor = sensor_parts[2]
								sub_sensor_parts = sensor.split('_')
								channel = sub_sensor_parts[-2]
								code = sub_sensor_parts[-1]
								aggr = sub_sensor_parts[1]
								new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
								val['params']['pawFields'].update({new_sensor_code:v})
								del val['params']['pawFields'][i]

							for i, v in enumerate(val['params']['sensors']):
								if v is None:
									continue
								sensor_parts = v.split('-')
								db = sensor_parts[0]
								if db == 'dg':
									print 'decagon sensor skipped.'
									continue
								station = sensor_parts[1]
								sensor = sensor_parts[2]
								sub_sensor_parts = sensor.split('_')
								channel = sub_sensor_parts[-2]
								code = sub_sensor_parts[-1]
								aggr = sub_sensor_parts[1]
								new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
								val['params']['sensors'][i] = new_sensor_code
								#iterate over paw values replace sensor code in at index 0
								for counter, value in enumerate(val['value']):
									if v == value[0]['sensor']:
										val['value'][counter][0]['sensor'] = new_sensor_code

						elif key in ['chilling_portions', 'degree_days', 'chilling_hours']:
							sensor_parts = val['params']['sensors'].split('-')
							db = sensor_parts[0]
							if db == 'dg':
								print 'decagon sensor skipped.'
								continue
							station = sensor_parts[1]
							sensor = sensor_parts[2]
							sub_sensor_parts = sensor.split('_')
							channel = sub_sensor_parts[-2]
							code = sub_sensor_parts[-1]
							aggr = sub_sensor_parts[1]
							new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
							val['params']['sensors'] = new_sensor_code
						elif key == 'dew_point':
							sensor_parts = val['params']['rh'].split('-')
							db = sensor_parts[0]
							if db == 'dg':
								print 'decagon sensor skipped.'
								continue
							station = sensor_parts[1]
							sensor = sensor_parts[2]
							sub_sensor_parts = sensor.split('_')
							channel = sub_sensor_parts[-2]
							code = sub_sensor_parts[-1]
							aggr = sub_sensor_parts[1]
							new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
							val['params']['rh'] = new_sensor_code

							sensor_parts = val['params']['temp'].split('-')
							db = sensor_parts[0]
							if db == 'dg':
								print 'decagon sensor skipped.'
								continue
							station = sensor_parts[1]
							sensor = sensor_parts[2]
							sub_sensor_parts = sensor.split('_')
							channel = sub_sensor_parts[-2]
							code = sub_sensor_parts[-1]
							aggr = sub_sensor_parts[1]
							new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
							val['params']['temp'] = new_sensor_code


						else:
							print 'processing ', key
							if val['params'].has_key('labels'):
								for i, v in val['params']['labels'].items():
									sensor_parts = i.split('-')
									db = sensor_parts[0]
									if db == 'dg':
										print 'decagon sensor skipped.'
										continue
									station = sensor_parts[1]
									sensor = sensor_parts[2]
									sub_sensor_parts = sensor.split('_')
									channel = sub_sensor_parts[-2]
									code = sub_sensor_parts[-1]
									aggr = sub_sensor_parts[1]
									new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
									val['params']['labels'].update({new_sensor_code:v})
									del val['params']['labels'][i]
							for i, v in enumerate(val['params']['sensors']):
								if v is None:
									continue
								sensor_parts = v.split('-')
								db = sensor_parts[0]
								if db == 'dg':
									print 'decagon sensor skipped.'
									continue
								station = sensor_parts[1]
								sensor = sensor_parts[2]
								sub_sensor_parts = sensor.split('_')
								channel = sub_sensor_parts[-2]
								code = sub_sensor_parts[-1]
								aggr = sub_sensor_parts[1]
								new_sensor_code = convert_sensor(station, channel, code, aggr, 'main-chart')
								val['params']['sensors'][i] = new_sensor_code
					except KeyError as e:
						print e
			old_widget['data'][key] = val
			print 'sensor list updated '
		widget_to_update = Widgets.objects.filter(widget_id=widget.widget_id, user=widget.user).update(widget=old_widget)
		print '1 widget updated'


def convert_sensor(station, channel, code, aggr, w_type):
	sensors = update_sensor_lst(station)
	print channel, code, aggr, station
	for sensor, name in sensors.iteritems():
		parts = sensor.split('_')
		new_channel = parts[0]
		new_code = parts[-2]
		new_aggr = parts[-1]
		if aggr == 'aver':
			aggr = 'avg'
		if new_channel == channel and new_code == code and new_aggr == aggr:
			if w_type == 'stat':
				return sensor
			else:
				return 'fc-'+station+'-'+sensor
