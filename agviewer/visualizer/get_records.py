import json, requests, time
from django.http import HttpResponse
from models import *
from django.contrib.auth.decorators import login_required
from visualizer.calculations import *
from visualizer.decagon import dayofyear, station_from_xml, convert, convert_sca
from datetime import timedelta, datetime
from visualizer.utils import *
from visualizer.tasks import get_data_dg, get_data_fc, parse_dxd, get_rid, update_sensor_lst
from django.db import IntegrityError
from colour import Color
# from visualizer.general import Alert

# globals
DAY = timedelta(days=1)
HOUR = timedelta(hours=1)


@login_required
def get_widget(request):
	print 'get_records.get_widget called'
	if request.is_ajax():
		if request.method == 'POST':
			post_data = json.loads(request.body)
			if Widgets.objects.filter(user=request.user, widget_id=post_data['id']).exists():
				new_widget = set_widget(post_data, request.user)
				index = new_widget['index'] if new_widget['index'] !='' else 99
				Widgets.objects.filter(user=request.user, widget_id=post_data['id']).update(widget=new_widget, index=index)
				return HttpResponse(json.dumps(new_widget))
			else:
				new_widget = set_widget(post_data, request.user)
				index = new_widget['index'] if new_widget['index'] !='' else 99
				try:
					dash = Dashboard.objects.get(user=request.user, active=True)
				except Dashboard.DoesNotExist as e:
					dash = Dashboard.objects.filter(user=request.user)[0]
				widget = Widgets(user=request.user, index=index, widget_id=new_widget['id'],\
				 widget_type=new_widget['type'], widget=new_widget, dashboard=dash)
				widget.save()
				return HttpResponse(json.dumps(new_widget))

	return HttpResponse(json.dumps(post_data)) # return http bad request

def set_widget(widget_dict, user):
	if widget_dict['type'] == 'stat':
		try:
			if widget_dict['data'].has_key('calc'):
				for k, v in widget_dict['data'].iteritems():
					if v['params']['data'] == 'degree_days_acc':
						widget_dict['data']['calc']['value'] = get_degree_days_acc(user, v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'temp_min':
						widget_dict['data']['calc']['value'] = temp_min(v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'temp_max':
						widget_dict['data']['calc']['value'] = temp_max(v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'temp_avg':
						widget_dict['data']['calc']['value'] = temp_avg(v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'chilling_hours_acc':
						widget_dict['data']['calc']['value'] = chilling_hours_acc(user, v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'chilling_portions':
						widget_dict['data']['calc']['value'] = get_cportions_acc(user, v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'rain_accumulation':
						widget_dict['data']['calc']['value'] = get_rain_accumulation(user, v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'rain_accumulation_24h':
						widget_dict['data']['calc']['value'] = get_rain_accumulation_24h(v['params']['db'], v['params']['station_id'], v['params']['sensor'])
					elif v['params']['data'] == 'temp_min1h':
						widget_dict['data']['calc']['value'] = temp_min1h(v['params']['db'], v['params']['station_id'], v['params']['sensor'])
		except KeyError as e:
			print 'KeyError in set_widget', e
			# print widget_dict
			return widget_dict

	elif widget_dict['type'] == 'main-chart':
		for key, val in widget_dict['data'].iteritems():
			if key == 'evapo':
				if val is not None:
					widget_dict['data']['evapo']['value'] = get_eto_data(widget_dict, user)
			elif key == 'paw':
				if val is not None:
					paw_data = get_paw_data(widget_dict, user)
					widget_dict['data']['paw']['value'] = paw_data
			elif key == 'raw_sensors':
				if val is not None:
					widget_dict['data']['raw_sensors']['value'] = get_raw_data(widget_dict, user)
			elif key == "dew_point":
				if val is not None:
					widget_dict['data']['dew_point']['value'] = get_dew_point_data(widget_dict, user)
			elif key == 'chilling_portions':
				if val is not None:
					cportions_data = get_cportions_data(widget_dict, user)
					widget_dict['data']['chilling_portions']['value'] = cportions_data
			elif key == 'chilling_hours':
				if val is not None:
					widget_dict['data']['chilling_hours']['value'] = get_chill_hours_data(widget_dict, user)
			elif key == 'degree_days':
				if val is not None:
					widget_dict['data']['degree_days']['value'] = get_degree_days_data(widget_dict, user)
			elif key == 'ex_ec':
				if val is not None:
					widget_dict['data']['ex_ec']['value'] = get_sat_ec_data(widget_dict, user)
			elif key == 'voltage':
				if val is not None:
					widget_dict['data']['voltage']['value'] = get_voltage_data(widget_dict, user)
	return widget_dict

def set_stat_widget(widget_data_id):
	from datetime import datetime
	try:
		widget_data = Data.objects.get(id=widget_data_id)
	except Data.DoesNotExist as e:
		return {
			'success': False,
			'message': e.message,
			'value': 'Error'
		}

	if widget_data.sensor is None and widget_data.chart is None:
		return {
			'success': False,
			'message': 'No input provided.',
			'value': 'Error'
		}

	if widget_data.function == 'min' or widget_data.function == 'max' or widget_data.function == 'avg':

		try:
			widget_id = widget_data.chart.widget_id if widget_data.chart is not None else None
			result = min_max_avg(widget_data.function, widget_data.sensor, widget_data.extract, widget_id,\
			 widget_data.date_from, widget_data.date_to)
		except Exception as e:
			return {
				'success': False,
				'message': e.message,
				'value': 'Error'
			}
		#save updated colums to the db
		widget_data.date_to = result['date_to']
		widget_data.value = result['value']
		widget_data.stale = result['stale']
		widget_data.save()

		return result

	elif widget_data.function == 'chill_hours_acc':
		#option only available for sensor
		if widget_data.sensor is None:
			return {
				'success': False,
				'message': e.message,
				'value': 'Error'
			}
		db = widget_data.sensor.split('-')[0]
		station = widget_data.sensor.split('-')[1]
		sensor = widget_data.sensor.split('-')[2]
		if db == 'dg':
			sensor = widget_data.sensor.split('-')[2]+'-'+widget_data.sensor.split('-')[3]

		result = stat_chill_hours_acc(widget_data.user, db, station, sensor)

		widget_data.value = result['value']
		widget_data.date_to = parse_date(result['date_to'])
		widget_data.save()
		return result

	elif widget_data.function == 'chill_portions':
		#option only available for sensor
		if widget_data.sensor is None:
			return {
				'success': False,
				'message': e.message,
				'value': 'Error'
			}
		db = widget_data.sensor.split('-')[0]
		station = widget_data.sensor.split('-')[1]
		sensor = widget_data.sensor.split('-')[2]
		if db == 'dg':
			sensor = widget_data.sensor.split('-')[2] +'-'+widget_data.sensor.split('-')[3]

		result = stat_cportions_acc(widget_data.user, db, station, sensor)

		widget_data.value = result['value']
		widget_data.date_to = parse_date(result['date_to'])
		widget_data.save()
		return result

	elif widget_data.function == 'degree_days_acc':
		#option only available for sensor
		if widget_data.sensor is None:
			return {
				'success': False,
				'message': e.message,
				'value': 'Error'
			}
		db = widget_data.sensor.split('-')[0]
		station = widget_data.sensor.split('-')[1]
		sensor = widget_data.sensor.split('-')[2]
		if db == 'dg':
			sensor = widget_data.sensor.split('-')[2] +'-'+widget_data.sensor.split('-')[3]

		result = stat_degree_days_acc(widget_data.user, db, station, sensor)

		widget_data.value = result['value']
		widget_data.date_to = parse_date(result['date_to'])
		widget_data.save()
		return result

	elif widget_data.function == 'last_record':
		#option only available for sensor

		if widget_data.sensor is None:
			return {
				'success': False,
				'message': 'Option only available for sensor',
				'value': 'Error'
			}
		db = widget_data.sensor.split('-')[0]
		station = widget_data.sensor.split('-')[1]
		sensor = widget_data.sensor.split('-')[2]
		if db == 'dg':
			sensor = widget_data.sensor.split('-')[2] +'-'+ widget_data.sensor.split('-')[3]

		data = StationData.objects.filter(station_id=station).last()
		present = datetime.now() - timedelta(hours=3)
		stale = False
		if data is not None:
			if db == 'fc':
				widget_data.value = data.data[sensor]
				widget_data.date_to = parse_date(data.data['date'])
				if present - widget_data.date_to > timedelta(hours=24):
					stale = True
				widget_data.stale = stale
				widget_data.save()
				return {
					'success': True, 
					'message': 'success', 
					'value': data.data[sensor], 
					'unit': '',
					'date_to': data.data['date'],
					'stale': stale
				}
			else:
				#183: Flow Meter Sensor, 222: LWS Leaf Wetness Sensor, 221: PS-1 Pressure switch
				#189: ECRN 50 mm, 187: ECRN 100, 188: ECRN 50 vol. ml
				if sensor.split('-')[0] in ['180', '183', '222', '221', '189', '187', '188']: 
					# print data.data, data.get_previous_by_date(station_id=station).data
					value = int(data.data[sensor]) - int(data.get_previous_by_date(station_id=station).data[sensor])
					#apply multiplier for 187: ECRN-100
					if sensor.split('-')[0] == '187':
						value *= 0.2
					#apply multiplier for 187: ECRN-50
					if sensor.split('-')[0] == '188':
						value *= 5
					value = round(convert_sca(value, sensor.split('-')[0], widget_data.extract ), 2)
					widget_data.value = value

					widget_data.date_to = parse_date(data.data['date'])
					if present - widget_data.date_to > timedelta(hours=24):
						stale = True
					widget_data.stale = stale
					widget_data.save()
					return {
						'success': True, 
						'message': 'success', 
						'value': widget_data.value, 
						'unit': '',
						'date_to': data.data['date'], 
						'stale': stale
					}	
				widget_data.value = round(convert_sca(int(data.data[sensor]), sensor.split('-')[0], widget_data.extract), 2)
				widget_data.date_to = parse_date(data.data['date'])
				if present - widget_data.date_to > timedelta(hours=24):
					stale = True
				widget_data.stale = stale
				widget_data.save()
				return {
					'success': True, 
					'message': 'success', 
					'value': widget_data.value, 
					'unit': '',
					'date_to': data.data['date'], 
					'stale': stale
				}

		else:
			return {
				'success': False, 
				'message': 'no data found',
				'value': None, 
				'unit': '',
				'date_to': None
			}
	elif widget_data.function == 'accumulation':

		try:
			widget_id = widget_data.chart.widget_id if widget_data.chart is not None else None
			result = sum_for_stat(widget_data.sensor, widget_data.extract, widget_id, widget_data.date_from, widget_data.date_to)
		except Exception as e:
			return {
				'success': False,
				'message': e.message,
				'value': 'Error'
			}
		#save updated colums to the db
		widget_data.date_to = result['date_to']
		widget_data.value = result['value']
		widget_data.stale = result['stale']
		widget_data.save()

		return result




def has_data(data_lst):
	i = 0
	if data_lst != []:
		while i < 10 and i < len(data_lst):
			if data_lst[i]['value'] == '':
				i +=1
			elif data_lst[i]['value'] != '':
				return True
		if i > 8:
			return False
	else:
		return False


def get_temp_data(user, db, station, dt_from, dt_to):
	print 'getting Temperature data'
	fc_sensors = ['0', '16385', '506', '20484', '20486', '20483', '21777']
	dg_sensors = ['252-1', '252-3', '241-1'] # update this!
	appuser = AppUser.objects.get(user=user)
	if db == 'fc':
		sensors = get_sensor_list(appuser, station)
		for k, v in sensors.iteritems():
			if k in fc_sensors:
				data_list = load_data(station, k, db, dt_from, dt_to)
				if has_data(data_list):
					return data_list
				else:
					return []
	elif db == 'dg':
		station_data = StationData.objects.filter(station_id=station, database='dg')
		if not station_data.exists():
			return False
		sensors = [k for k, v in station_data[0].data.iteritems()]
		for sensor in sensors:
			if sensor in dg_sensors:
				print True
				data_list = load_data(station, sensor, db, dt_from, dt_to)
				if has_data(data_list):
					data_lst = [{
						'date':rec['date'], 
						'value':convert(float(rec['value']), sensor.split('-')[0], 'temp') if rec['value'] != '' else rec['value']} for rec in data_list]
					return data_lst

	return False

def min_max_avg(function, sensor, extract, chart, dt_from, dt_to):

	data = None
	value_lst = []
	stale = False

	if sensor is not None:
		#break up sensor into parts
		try:
			db = sensor.split('-')[0]
			station = sensor.split('-')[1]
			sensor_code = sensor.split('-')[2]
		except Exception as e:
			return {
				'success': False, 
				'message': e.message,
				'value': None,
				'date_to': None, 
				'stale': stale
			}
		if db == 'fc':
			data = load_data(station, sensor_code, db, dt_from, dt_to)
			if len(data) < 1:
				duration = dt_to - dt_from
				last_record = StationData.objects.filter(station_id=station).last()
				if last_record is None:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None, 
						'stale': stale

					}
				dt_to = last_record.date
				dt_from = dt_to - duration

				data = load_data(station, sensor_code, db, dt_from, dt_to)
				if len(data) < 1:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None,
						'stale': True
					}
				stale = True

		elif db == 'dg':
			data = load_data(station, sensor_code+'-'+sensor.split('-')[3], db, dt_from, dt_to)
			#222: LWS Leaf Wetness Sensor, 183: Flow Meter Sensor, 221: PS-1 Pressure Switch
			#189: ECRN-50.Perc.[mm]
			if sensor_code in ['222', '180', '183', '221', '189']:
				accum_data = get_hourly_sum(data, 1)
				data = accum_data
			#187: ECRN-100.Perc.[mm]
			if sensor_code in ['187']:
				accum_data = get_hourly_sum(data, 0.2)
				data = accum_data
			#188: ECRN-50.Perc.vol.[ml]
			if sensor_code in ['188']:
				accum_data = get_hourly_sum(data, 5)
				data = accum_data
			if len(data) < 1:
				duration = dt_to - dt_from
				last_record = StationData.objects.filter(station_id=station).last()
				if last_record is None:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None,
						'stale': stale
					}
				dt_to = last_record.date
				dt_from = dt_to - duration

				data = load_data(station, sensor_code+'-'+sensor.split('-')[3], db, dt_from, dt_to)

				if len(data) < 1:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None,
						'stale': stale
					}
				stale = True

		for record in data:
			if db == 'fc':
				try:
					value_lst.extend([float(record['value'])])
				except Exception as e:
					continue
			else:
				try: 
					#split sensor_code to get decagon sensor code
					value_lst.extend([convert_sca(int(record['value']), sensor_code, extract)])
				except Exception as e:
					print e.message
					continue

	if chart is not None:
		
		data = get_data_from_chart(chart, dt_from, dt_to)

		for record in data:
			try:
				value_lst.extend([float(record['value'])])
			except Exception as e:
				continue

	# if chart is None :
	# 	return {
	# 		'success': False, 
	# 		'message': 'No chart or sensor selected.',
	# 		'value': None,
	# 		'date_to': None,
	# 		'stale': stale
	# 	}

	if len(value_lst) < 1:
		return {
			'success': False, 
			'message': 'No input provided.',
			'value': None,
			'date_to': None,
			'stale': stale
		}
	
	last_record_date = data[len(data)-1]['date']


	if function == 'min':
		try:
			result = min(value_lst)
			# print value_lst
			# print result
		except Exception as e:
			return {
				'success': False, 
				'message': e.message,
				'value': None,
				'date_to': last_record_date,
				'stale': stale
			}
		return {
			'success': True, 
			'message': '',
			'value': round(result, 2),
			'unit': '',
			'date_to': last_record_date,
			'stale': stale
		}
	elif function == 'max':
		try:
			result = max(value_lst)
		except Exception:
			return {
				'success': False, 
				'message': e.message,
				'value': None,
				'date_to': last_record_date,
				'stale': stale
			}
		return {
			'success': True, 
			'message': '',
			'value': round(result, 2),
			'unit': '',
			'date_to': last_record_date,
			'stale': stale
		}
	elif function == 'avg':
		try:
			result = sum(value_lst)/len(value_lst)
		except Exception:
			return {
				'success': False, 
				'message': e.message,
				'value': None,
				'date_to': last_record_date,
				'stale': stale
			}
		return {
			'success': True, 
			'message': '',
			'value': round(result, 2),
			'unit': '',
			'date_to': last_record_date,
			'stale': stale
		}

def sum_for_stat(sensor, extract, chart, dt_from, dt_to):
	
	value_lst = []
	stale = False
	if chart is not None:

		data = get_data_from_chart(chart, dt_from, dt_to)
		# print data

		for record in data:
			try:
				value_lst.extend([float(record['value'])])
			except Exception as e:
				continue
		
		# print value_lst
		result = sum(value_lst)

		return {
			'success': True, 
			'message': '',
			'value': round(result, 2),
			'unit': '',
			'date_to': data[-1]['date'],
			'stale': stale
		}

	if sensor is not None:
		#break up sensor into parts
		try:
			db = sensor.split('-')[0]
			station = sensor.split('-')[1]
			sensor_code = sensor.split('-')[2]
		except Exception as e:
			return {
				'success': False, 
				'message': e.message,
				'value': None,
				'date_to': None, 
				'stale': stale
			}
		if db == 'fc':
			data = load_data(station, sensor_code, db, dt_from, dt_to)
			if len(data) < 1:
				duration = dt_to - dt_from
				last_record = StationData.objects.filter(station_id=station).last()
				if last_record is None:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None, 
						'stale': stale

					}
				dt_to = last_record.date
				dt_from = dt_to - duration

				data = load_data(station, sensor_code, db, dt_from, dt_to)
				if len(data) < 1:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None,
						'stale': True
					}
				stale = True

		elif db == 'dg':
			data = load_data(station, sensor_code+'-'+sensor.split('-')[3], db, dt_from, dt_to)
			if len(data) < 1:
				duration = dt_to - dt_from
				last_record = StationData.objects.filter(station_id=station).last()
				if last_record is None:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None,
						'stale': stale
					}
				dt_to = last_record.date
				dt_from = dt_to - duration

				data = load_data(station, sensor_code+'-'+sensor.split('-')[3], db, dt_from, dt_to)

				if len(data) < 1:
					return {
						'success': False, 
						'message': 'No input provided.',
						'value': None,
						'date_to': None,
						'stale': stale
					}
				stale = True
			#222: LWS Leaf Wetness Sensor, 183: Flow Meter Sensor, 221: PS-1 Pressure Switch
			#189: ECRN-50.Perc.[mm]
			if sensor_code in ['222', '180', '183', '221', '189']:
				accum_data = get_hourly_sum(data, 1)
				data = accum_data
			#187: ECRN-100.Perc.[mm]
			if sensor_code in ['187']:
				accum_data = get_hourly_sum(data, 0.2)
				data = accum_data
			#188: ECRN-50.Perc.vol.[ml]
			if sensor_code in ['188']:
				accum_data = get_hourly_sum(data, 5)
				data = accum_data
		for record in data:
			if db == 'fc':
				try:
					value_lst.extend([float(record['value'])])
				except Exception as e:
					print e.message
					continue
			else:
				try: 
					#split sensor_code to get decagon sensor code
					value_lst.extend([convert_sca(int(record['value']), sensor_code, extract)])
				except Exception as e:
					print e.message
					continue

		# print value_lst
		result = sum(value_lst)

		dt_to = parse_date(data[-1]['date'])

		return {
			'success': True, 
			'message': '',
			'value': round(result, 2),
			'unit': '',
			'date_to': date_to_string(dt_to),
			'stale': stale
		}





def get_data_from_chart(chart_id, dt_from, dt_to):

	try:
		chart = Widgets.objects.get(widget_id=chart_id).widget
	except Exception as e:
		return []

	for key, data in chart['data'].iteritems():
		#skip non-data items
		if key in ['title', 'range', 'calc']:
			continue

		if data is not None:
			#if empty move on
			if data['value'] is None:
				continue
			if len(data['value']) < 1:
				continue

			duration = dt_to - dt_from

			if key in ['raw_sensors', 'ex_ec', 'paw', 'voltage']:
				#if empty move on

				if len(data['value'][0]) < 1:
					continue

				if dt_to >= parse_date(data['value'][0][-1]['date']):

					dt_from = parse_date(data['value'][0][-1]['date']) - duration
					dt_to = parse_date(data['value'][0][-1]['date'])

				values = []

				for v in data['value'][0]:
					if dt_from <= parse_date(v['date']) <= dt_to:
						values.extend([v])

				return values

			elif key in ['dew_point', 'evapo']:
				#if empty move on

				if data['value'] is None:
					continue
				if len(data['value']) < 1:
					continue

				if dt_to >= parse_date(data['value'][-1]['date']):
					dt_from = parse_date(data['value'][-1]['date']) - duration
					dt_to = parse_date(data['value'][-1]['date'])

				values = []
				
				for v in data['value']:
					if dt_from <= parse_date(v['date']) <= dt_to:
						values.extend([v])

				return values
			#no chart calculation for degree days, chill hours and portions
			else: 
				return []

	return []




def temp_min(db, station, sensor):
	global HOUR
	period = 24
	records = StationData.objects.filter(station_id=station, database=db)
	if not records.exists():
		return '--'
	max_entry = records.last().date
	dt_from = max_entry - timedelta(hours=period)
	records = records.filter(date__range=(dt_from, max_entry)).values('data')
	if db == 'fc':
		value_lst = [float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0) for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		value_lst = [convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract) for rec in records]
	return round(min(value_lst), 2)

def temp_min1h(db, station, sensor):
	global HOUR
	period = 1
	records = StationData.objects.filter(station_id=station, database=db)
	if not records.exists():
		return '--'
	max_entry = records.last().date
	dt_from = max_entry - timedelta(hours=period)
	records = records.filter(date__range=(dt_from, max_entry)).values('data')
	if db == 'fc':
		value_lst = [float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0) for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		value_lst = [convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract) for rec in records]
	return round(min(value_lst), 2)


def temp_max(db, station, sensor):
	global HOUR
	period = 24
	records = StationData.objects.filter(station_id=station, database=db)
	if not records.exists():
		return '--'
	max_entry = records.last().date
	dt_from = max_entry - timedelta(hours=period)
	records = records.filter(date__range=(dt_from, max_entry)).values('data')
	if db == 'fc':
		value_lst = [float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0) for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		value_lst = [convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract) for rec in records]
	return round(max(value_lst), 2)

def temp_avg(db, station, sensor):
	global HOUR
	period = 24
	records = StationData.objects.filter(station_id=station, database=db)
	if not records.exists():
		return '--'
	max_entry = records.last().date
	dt_from = max_entry - timedelta(hours=period)
	records = records.filter(date__range=(dt_from, max_entry)).values('data')
	if db == 'fc':
		value_lst = [float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0) for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		value_lst = [convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract) for rec in records]	
	return round(sum(value_lst)/len(value_lst),2)
	

def stat_degree_days_acc(user, db, station, sensor):
	global HOUR
	entries = StationData.objects.filter(station_id=station, database=db)
	if entries.exists():
		max_entry = entries.last().date
		min_entry = entries.first().date
	RESET_DATE = '01-01 08:00'
	YEAR = str(max_entry.year)
	threshold = 7
	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.ddays['dd_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	dt_from = parse_date(YEAR +'-'+RESET_DATE)
	
	#set dt_from to previous year
	if max_entry < dt_from:
		YEAR = str(int(YEAR)-1)
		dt_from = parse_date(YEAR +'-'+RESET_DATE)	

	try:
		settings = Settings.objects.get(user=user)
		threshold = int(settings.ddays['dd_threshold'])
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'

	if dt_from < min_entry:
		dt_from = min_entry
	records = entries.filter(date__range=(dt_from, max_entry)).values('data')
	if not records.exists():
		return {
			'success': False,
			'message': 'No data provided.',
			'value': None
		}
	temp_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
	# if db == 'fc':
	# 	temp_data = [{
	# 		'date': json.loads(rec['data'])['date'],
	# 		'value':float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0)} for rec in records]
		daily_avg = get_daily_avg(temp_data)
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		# temp_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract)} for rec in records]
		daily_avg = get_daily_avg(temp_data)
	degree_days_acc = calculate_degree_days(daily_avg, threshold, RESET_DATE)
	# return round(degree_days_acc[len(degree_days_acc)-1]['value'], 1)
	return {
		'success': True,
		'value': round(degree_days_acc[len(degree_days_acc)-1]['value'], 1), 
		'message': '',
		'date_to': degree_days_acc[len(degree_days_acc)-1]['date'], 
		'unit': ''
	}

def get_degree_days_acc(user, db, station, sensor):
	global HOUR
	entries = StationData.objects.filter(station_id=station, database=db)
	if entries.exists():
		max_entry = entries.last().date
		min_entry = entries.first().date
	RESET_DATE = '01-01 08:00'
	YEAR = str(max_entry.year)
	threshold = 7
	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.ddays['dd_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	dt_from = parse_date(YEAR +'-'+RESET_DATE)
	
	#set dt_from to previous year
	if max_entry < dt_from:
		YEAR = str(int(YEAR)-1)
		dt_from = parse_date(YEAR +'-'+RESET_DATE)	

	try:
		settings = Settings.objects.get(user=user)
		threshold = int(settings.ddays['dd_threshold'])
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'

	if dt_from < min_entry:
		dt_from = min_entry
	records = entries.filter(date__range=(dt_from, max_entry)).values('data')
	if not records.exists():
		return '--'
	temp_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
	# if db == 'fc':
	# 	temp_data = [{
	# 		'date': json.loads(rec['data'])['date'],
	# 		'value':float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0)} for rec in records]
		daily_avg = get_daily_avg(temp_data)
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		# temp_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract)} for rec in records]
		daily_avg = get_daily_avg(temp_data)
	degree_days_acc = calculate_degree_days(daily_avg, threshold, RESET_DATE)
	return round(degree_days_acc[len(degree_days_acc)-1]['value'], 1)



def stat_chill_hours_acc(user, db, station, sensor):
	entries = StationData.objects.filter(station_id=station, database=db)
	if entries.exists():
		max_entry = entries.last().date
		min_entry = entries.first().date
	RESET_DATE = '01-01 08:00'
	YEAR = str(max_entry.year)
	threshold = 7
	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.chours['ch_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	dt_from = parse_date(YEAR +'-'+RESET_DATE)

	#set dt_from to previous year
	if max_entry < dt_from:
		YEAR = str(int(YEAR)-1)
		dt_from = parse_date(YEAR +'-'+RESET_DATE)	

	try:
		settings = Settings.objects.get(user=user)
		threshold = int(settings.chours['ch_threshold'])
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'

	if dt_from < min_entry:
		dt_from = min_entry
	print dt_from
	records = entries.filter(date__range=(dt_from, max_entry)).values('data')
	if not records.exists():
		return {
			'success': False,
			'message': 'No data provided.',
			'value': None
		}

	temp_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
		# temp_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':float(json.loads(rec['data'])[sensor] if json.loads(rec['data'])[sensor] is not None else 0)} for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		# temp_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract)} for rec in records]
	chill_hours_acc = calculate_chill_hours(temp_data, threshold, RESET_DATE)

	return {
			'success': True,
			'value':chill_hours_acc[len(chill_hours_acc)-1]['value'], 
			'message': '',
			'date_to': chill_hours_acc[len(chill_hours_acc)-1]['date'], 
			'unit': ''
		}

def chilling_hours_acc(user, db, station, sensor):
	entries = StationData.objects.filter(station_id=station, database=db)
	if entries.exists():
		max_entry = entries.last().date
		min_entry = entries.first().date
	RESET_DATE = '01-01 08:00'
	YEAR = str(max_entry.year)
	threshold = 7
	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.chours['ch_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	dt_from = parse_date(YEAR +'-'+RESET_DATE)

	#set dt_from to previous year
	if max_entry < dt_from:
		YEAR = str(int(YEAR)-1)
		dt_from = parse_date(YEAR +'-'+RESET_DATE)	

	try:
		settings = Settings.objects.get(user=user)
		threshold = int(settings.chours['ch_threshold'])
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'

	if dt_from < min_entry:
		dt_from = min_entry
	print dt_from
	records = entries.filter(date__range=(dt_from, max_entry)).values('data')
	if not records.exists():
		return '--'
	temp_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
		# temp_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':float(json.loads(rec['data'])[sensor] if json.loads(rec['data'])[sensor] is not None else 0)} for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				temp_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		# temp_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract)} for rec in records]
	# print temp_data
	chill_hours_acc = calculate_chill_hours(temp_data, threshold, RESET_DATE)
	# print chill_hours_acc
	return chill_hours_acc[len(chill_hours_acc)-1]['value']

def stat_cportions_acc(user, db, station, sensor):
	entries = StationData.objects.filter(station_id=station, database=db)
	if entries.exists():
		max_entry = entries.last().date
		min_entry = entries.first().date
	else:
		return {
			'success': False,
			'message': 'No data provided.',
			'value': None
		}

	RESET_DATE = '01-01 08:00'
	YEAR = str(max_entry.year)
	
	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.cportions['cp_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	dt_from = parse_date(YEAR +'-'+RESET_DATE)

	#set dt_from to previous year
	if max_entry < dt_from:
		YEAR = str(int(YEAR)-1)
		dt_from = parse_date(YEAR +'-'+RESET_DATE)	

	print dt_from
	records = entries.filter(date__range=(dt_from, max_entry)).values('data')
	raw_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
	# if db == 'fc':
	# 	raw_data = [{
	# 		'date': json.loads(rec['data'])['date'],
	# 		'value':float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0)} for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		# raw_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract)} for rec in records]
	# print raw_data
	cportions_data = calculate_cportions(get_hourly_avg(raw_data,0,1), RESET_DATE)
	# return int(cportions_data[len(cportions_data)-1]['accumulation'])
	return {
		'success': True,
		'value': round(cportions_data[-1]['accumulation']),
		'message': '',
		'date_to': raw_data[-1]['date'],
		'unit': ''
	}

def get_cportions_acc(user, db, station, sensor):
	entries = StationData.objects.filter(station_id=station, database=db)
	if entries.exists():
		max_entry = entries.last().date
		min_entry = entries.first().date
	else:
		return 'no data'

	RESET_DATE = '01-01 08:00'
	YEAR = str(max_entry.year)
	
	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.cportions['cp_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	dt_from = parse_date(YEAR +'-'+RESET_DATE)

	#set dt_from to previous year
	if max_entry < dt_from:
		YEAR = str(int(YEAR)-1)
		dt_from = parse_date(YEAR +'-'+RESET_DATE)	

	print dt_from
	records = entries.filter(date__range=(dt_from, max_entry)).values('data')
	raw_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
	# if db == 'fc':
	# 	raw_data = [{
	# 		'date': json.loads(rec['data'])['date'],
	# 		'value':float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0)} for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'temp'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		# raw_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract)} for rec in records]
	# print raw_data
	cportions_data = calculate_cportions(get_hourly_avg(raw_data, 0, 1), RESET_DATE)
	return int(cportions_data[len(cportions_data)-1]['accumulation'])


def get_rain_accumulation(user, db, station, sensor):
	entries = StationData.objects.filter(station_id=station, database=db)
	if entries.exists():
		max_entry = entries.last().date
		min_entry = entries.first().date
	else:
		return 'no data'

	RESET_DATE = '01-01 08:00'
	YEAR = str(max_entry.year)

	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.arain['ar_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	dt_from = parse_date(YEAR +'-'+RESET_DATE)

	#set dt_from to previous year
	if max_entry < dt_from:
		YEAR = str(int(YEAR)-1)
		dt_from = parse_date(YEAR +'-'+RESET_DATE)

	records = entries.filter(date__range=(dt_from, max_entry)).values('data')

	if not records.exists():
		return 'no data'

	raw_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
	# if db == 'fc':
	# 	raw_data = [{
	# 		'date': json.loads(rec['data'])['date'],
	# 		'value':float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0)} for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'rain'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		if code == '187':
			print 'ecrn 100 accumulation'
			# ecrn 100 accumulation
			raw_data_acc = get_hourly_sum(raw_data, 0.2)
			raw_data = raw_data_acc
			raw_data_acc = None
		# raw_data = [{
		# 	'date': json.loads(rec['data'])['date'],
		# 	'value':convert_sca(float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0),code,extract)} for rec in records]

	
	rain_accumulation = 0
	for data in raw_data:
		if data['value'] is None:
			continue
		rain_accumulation += data['value']
		# print data['date'], data['value'], rain_accumulation

	return round(rain_accumulation, 1)

def get_rain_accumulation_24h(db, station, sensor):
	period = 24
	records = StationData.objects.filter(station_id=station, database=db)
	if not records.exists():
		return 'no data'
	max_entry = records.last().date
	dt_from = max_entry - timedelta(hours=period)
	records = records.filter(date__range=(dt_from, max_entry)).values('data')
	if not records.exists():
		return 'no data'

	raw_data = []
	if db == 'fc':
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': value }])
			except KeyError as e:
				print e
	# if db == 'fc':
	# 	raw_data = [{
	# 		'date': json.loads(rec['data'])['date'],
	# 		'value':float(json.loads(rec['data'])[sensor] and json.loads(rec['data'])[sensor] or 0)} for rec in records]
	else:
		code = sensor.split('-')[0]
		extract = 'rain'
		for rec in records:
			try:
				value = float(json.loads(rec['data'])[sensor]) if json.loads(rec['data'])[sensor] is not None else None
				raw_data.extend([{'date': json.loads(rec['data'])['date'], 'value': convert_sca(value, code, extract) }])
			except KeyError as e:
				print e
		if code == '187':
			print 'ecrn 100 accumulation'
			# ecrn 100 accumulation
			raw_data_acc = get_hourly_sum(raw_data, 0.2)
			raw_data = raw_data_acc
			raw_data_acc = None

	rain_accumulation = 0
	for data in raw_data:
		if data['value'] is None:
			continue
		rain_accumulation += data['value']

	return round(rain_accumulation, 1)







def get_raw_data(widget_data, user):
	global DAY
	daily_avg = []
	params = widget_data['data']['raw_sensors']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	chart_type = "line"
	line_color = ""
	sensor_name = ""
	station_name = ""
	
	if params.has_key('sensors'):
		sensors = params['sensors']
		if len(sensors) == 1:
			try:
				settings = Settings.objects.get(user=user)
				chart_type = settings.sensor_graph[sensors[0]]
			except (KeyError, Settings.DoesNotExist):
				print 'KeyError or DoesNotExist'
			try:
				settings = Settings.objects.get(user=user)
				line_color = settings.sensor_color[sensors[0]]
			except (KeyError, Settings.DoesNotExist):
				print 'KeyError or DoesNotExist'
			sens = sensors[0].split('-')
			station = Stations.objects.filter(user=user, station=sens[1])
			if station.exists():
				if station[0].sensors.has_key(sens[2]):
					sensor_name = station[0].sensors[sens[2]]
				if sens[0] == 'dg':
					if station[0].sensors.has_key(sens[2]+'-'+sens[3]):
						sensor_name = station[0].sensors[sens[2]+'-'+sens[3]]
				 #get sensor name to inject

			#get user's alerts
			# alerts = Alert.has_alerts(user, sensors[0], None)

			axis_name = sensor_name
			if sens[0] == 'fc':
				try:
					axis_code = sens[2].split('_')[-2]
				except IndexError as e:
					print e
					axis_code = sens[2].split('_')[-1]

				try:
					sensor_code = SensorCodes.objects.get(sensor_id=axis_code)
					if sensor_code.axis_name != '':
						axis_name = sensor_code.axis_name
					if sensor_code.axis_code != '':
						axis_code = sensor_code.axis_code
				except SensorCodes.DoesNotExist as e:
					print e
				sensor_data = load_data(sens[1], sens[2], sens[0], dt_from, dt_to)
				
				# #watch for alert events
				# for d in sensor_data:
				# 	for a in alerts:
				# 		event = {
				# 			'value': d['value'] if d['value'] is not None else 0,
				# 			'date': d['date'],
				# 			'widget_id': widget_data['id'],
				# 			'sensor': sensors
				# 		}
				# 		alert = Alert.alert_from_model_obj(a)
				# 		alert.watch(event, sensors[0], None)

				#if no data return emptry list (handle gracefully)
				if len(sensor_data) < 1:
					return []

				sensor_data[0].update({
					'axis_name':axis_name,
					'axis_id': axis_code,
					'station':sens[1],
					'type':chart_type,
					'lineColor':line_color,
					'suffix':'',
					'label_id':sensors[0]}) # insert sensor code into the first entry
				daily_avg.extend([sensor_data])

				#hanlde fc multi graph requirement
				# (leaf wetness daily accum.)
				leaf_wetness_sensors = SensorCodes.objects.filter(sensor_name__iregex=r'(leaf\swetness)|(wetness\sleaf)|(humedad\sde\shuja)')
				leaf_wetness_codes = [rec.sensor_id for rec in leaf_wetness_sensors]
				# print leaf_wetness_codes
				try:
					if sens[2].split('_')[-2] in leaf_wetness_codes:
						print 'calculating leaf wetness daily accum'
						lighter_color = Color(line_color)
						if line_color != '':
							# print lighter_color.luminance
							if 1 - lighter_color.luminance > 0.2:
								lighter_color.luminance += 0.2
							else:
								lighter_color.luminance -= 0.2
							# print lighter_color.luminance
						daily_accum = get_sum(sensor_data, 0, 0, 24)

						if len(daily_accum) > 0:
							daily_accum[0].update({
								'axis_name':axis_name,
								'axis_id': axis_code,
								'station':sens[1],
								'type':chart_type,
								'lineColor':lighter_color.hex,
								'suffix':' sum',
								'label_id':sensors[0], 
								'valueOnBar':True})
						daily_avg.extend([daily_accum])
				except IndexError as e:
					print e

			elif sens[0] == 'dg':
				axis_name = ''
				axis_code = sens[2]
				try:
					sensor_code = SensorCodes.objects.get(sensor_id=sens[2])
					if sensor_code.axis_name != '':
						axis_name = sensor_code.axis_name
					if sensor_code.axis_code != '':
						axis_code = sensor_code.axis_code
				except SensorCodes.DoesNotExist as e:
					print e
				sensor_data = load_data(sens[1], sens[2]+'-'+sens[3], sens[0], dt_from, dt_to)
				
				#if no data return emptry list (handle gracefully)
				if len(sensor_data) < 1:
					return []

				comp_values = make_list(sensor_data, sens[2])
				graph_suffix = ''
				value_on_bar = False
				for k, v in comp_values.iteritems():

					#watch for alert events
					# for d in v:
					# 	for a in alerts:
					# 		event = {
					# 			'value': d['value'] if d['value'] is not None else 0,
					# 			'date': d['date'],
					# 			'widget_id': widget_data['id'],
					# 			'sensor': sensors
					# 		}
					# 		alert = Alert.alert_from_model_obj(a)
					# 		alert.watch(event, sensors[0], None)

					if len(k.split(' ')) > 1:
						axis_code = k.split(' ')[len(k.split(' '))-1].lower()
						graph_suffix = k.split(' ')[len(k.split(' '))-1]
					if k == 'PS-1.sum':
						graph_suffix = k.split('.')[-1]
						value_on_bar = True
						lighter_color = Color(line_color)
						if line_color != '':
							if 1 - lighter_color.luminance > 0.2:
								lighter_color.luminance += 0.2
							else:
								lighter_color.luminance -= 0.2
							line_color = lighter_color.hex
						else:
							line_color = ''
					v[0].update({
						'axis_name':k.split(' ')[len(k.split(' '))-1] if axis_name == '' else axis_name,
						'axis_id': axis_code,
						'station':sens[1],
						'type':chart_type,
						'lineColor':line_color,
						'suffix':graph_suffix,
						'label_id':sensors[0], 
						'valueOnBar': value_on_bar})
					daily_avg.extend([v])
		elif len(sensors) > 1:
			for i, v in enumerate(sensors):
				#get user's alerts
				# alerts = Alert.has_alerts(user, v, None)
				# print 'has alerts', v
				# print alerts
				sens = v.split('-')
				chart_type ='line'
				line_color =''
				try:
					settings = Settings.objects.get(user=user)
					chart_type = settings.sensor_graph[v]
				except (KeyError, Settings.DoesNotExist):
					print 'KeyError or DoesNotExist'
				try:
					settings = Settings.objects.get(user=user)
					line_color = settings.sensor_color[v]
				except (KeyError, Settings.DoesNotExist):
					print 'KeyError or DoesNotExist'

				station = Stations.objects.filter(user=user, station=sens[1])
				if station.exists():
					if station[0].sensors.has_key(sens[2]):
						sensor_name = station[0].sensors[sens[2]]
					if sens[0] == 'dg':
						if station[0].sensors.has_key(sens[2]+'-'+sens[3]):
							sensor_name = station[0].sensors[sens[2]+'-'+sens[3]]
				axis_name = sensor_name
				if sens[0] == 'fc':
					try:
						axis_code = sens[2].split('_')[-2]
					except IndexError as e:
						print e
						axis_code = sens[2].split('_')[-1]

					try:
						sensor_code = SensorCodes.objects.get(sensor_id=axis_code)
						if sensor_code.axis_name != '':
							axis_name = sensor_code.axis_name
						if sensor_code.axis_code != '':
							axis_code = sensor_code.axis_code
					except SensorCodes.DoesNotExist as e:
						print e
					sensor_data = load_data(sens[1], sens[2], sens[0], dt_from, dt_to)

					#watch for alert events
					# for d in sensor_data:
					# 	for a in alerts:
					# 		event = {
					# 			'value': d['value'] if d['value'] is not None else 0,
					# 			'date': d['date'],
					# 			'widget_id': widget_data['id'],
					# 			'sensor': [v]
					# 		}
					# 		alert = Alert.alert_from_model_obj(a)
					# 		alert.watch(event, v, None)

					#if no data return emptry list (handle gracefully)
					if len(sensor_data) < 1:
						sensor_data.extend([{'axis_name':axis_name,
							'axis_id': axis_code,
							'station':sens[1],
							'type':chart_type,
							'lineColor':line_color,
							'suffix':'',
							'label_id':v}])
						daily_avg.extend([sensor_data])
						continue

					sensor_data[0].update({
						'axis_name':axis_name,
						'axis_id': axis_code,
						'station':sens[1],
						'type':chart_type,
						'lineColor':line_color,
						'suffix':'',
						'label_id':v}) # insert sensor code into the first entry
					daily_avg.extend([sensor_data])

					#hanlde fc multi graph requirement
					# (leaf wetness daily accum.)
					leaf_wetness_sensors = SensorCodes.objects.filter(sensor_name__iregex=r'(leaf\swetness)|(wetness\sleaf)|(humedad\sde\shuja)')
					leaf_wetness_codes = [rec.sensor_id for rec in leaf_wetness_sensors]
					try:
						if sens[2].split('_')[-2] in leaf_wetness_codes:
							print 'calculating leaf wetness daily accum'
							lighter_color = Color(line_color)
							if line_color != '':
								# print lighter_color.luminance
								if 1 - lighter_color.luminance > 0.2:
									lighter_color.luminance += 0.2
								else:
									lighter_color.luminance -= 0.2
								# print lighter_color.luminance
							daily_accum = get_sum(sensor_data, 0, 0, 24)
							if len(daily_accum) > 0:
								daily_accum[0].update({
									'axis_name':axis_name,
									'axis_id': axis_code,
									'station':sens[1],
									'type':chart_type,
									'lineColor':lighter_color.hex,
									'suffix':' sum',
									'label_id':v, 
									'valueOnBar':True})
							daily_avg.extend([daily_accum])
					except IndexError as e:
						print e

				elif sens[0] == 'dg':
					axis_code = sens[2]
					axis_name = ''
					try:
						sensor_code = SensorCodes.objects.get(sensor_id=sens[2])
						if sensor_code.axis_name != '':
							axis_name = sensor_code.axis_name
						if sensor_code.axis_code != '':
							axis_code = sensor_code.axis_code
					except SensorCodes.DoesNotExist as e:
						print e
					sensor_data = load_data(sens[1], sens[2]+'-'+sens[3], sens[0], dt_from, dt_to)

					#if no data return emptry list (handle gracefully)
					if len(sensor_data) < 1:
						sensor_data.extend([{'axis_name':axis_name,
							'axis_id': axis_code,
							'station':sens[1],
							'type':chart_type,
							'lineColor':line_color,
							'suffix':'',
							'label_id':v}])
						daily_avg.extend([sensor_data])
						continue

					comp_values = make_list(sensor_data, sens[2])
					graph_suffix = ''
					value_on_bar = False
					for key, val in comp_values.iteritems():
						#watch for alert events
						# for d in val:
						# 	for a in alerts:
						# 		event = {
						# 			'value': d['value'] if d['value'] is not None else 0,
						# 			'date': d['date'],
						# 			'widget_id': widget_data['id'],
						# 			'sensor': [v]
						# 		}
						# 		alert = Alert.alert_from_model_obj(a)
						# 		alert.watch(event, v, None)

						if len(key.split(' ')) > 1:
							axis_code = key.split(' ')[len(key.split(' '))-1].lower()
							graph_suffix = key.split(' ')[len(key.split(' '))-1]
						if key == 'PS-1.sum':
							graph_suffix = key.split('.')[-1]
							value_on_bar = True
							lighter_color = Color(line_color)
							if line_color != '':
								if 1 - lighter_color.luminance > 0.2:
									lighter_color.luminance += 0.2
								else:
									lighter_color.luminance -= 0.2
								line_color = lighter_color.hex
							else:
								line_color = ''
						val[0].update({
							'axis_name':key.split(' ')[len(key.split(' '))-1] if axis_name == '' else axis_name,
							'axis_id': axis_code,
							'station':sens[1],
							'type':chart_type,
							'lineColor':line_color,
							'suffix':graph_suffix,
							'label_id':v,
							'valueOnBar': value_on_bar})
						daily_avg.extend([val])
	else:
		pass
	return daily_avg


def make_list(data, code):
	if code == '221': #if a PS-1 sensor
		return {'PS-1': get_hourly_sum(data, 1), 'PS-1.sum': get_daily_sum(data, 0, 0)}
	if code == '189': #if a ECRN-50.Perc.[mm]
		return {'ECRN-50.Perc.[mm]': get_hourly_sum(data, 1)}
	if code == '187': #if a ECRN-100
		return {'ECRN-100.Perc.[mm]': get_hourly_sum(data, 0.2)}
	if code == '188': #if a ECRN-50
		return {'ECRN-50.Perc.vol.[ml]': get_hourly_sum(data, 5)}
	#Flow Meter
	if code == '183':
		accum_data = get_quarterly_sum(data,1)
		return {
			'Flow.Meter.[L/s]': [{'date': rec['date'],
			'value':convert_sca(int(rec['value']), code, 'flow')} for rec in accum_data]
			}
	#Flow Meter
	if code == '180':
		accum_data = get_hourly_sum(data,1)
		return {
			'Flow.Meter.[L/H]': [{'date': rec['date'],
			'value':convert_sca(int(rec['value']), code, 'flow')} for rec in accum_data]
			}
	#LWS Leaf Wetness
	if code == '222':
		accum_data = get_hourly_sum(data,1)
		return {
			'LWS.Leaf.Wetness[Min]': [{'date': rec['date'],
			'value':convert_sca(int(rec['value']), code, '')} for rec in accum_data]
			}
	values = {}
	for record in data:
		if record['value'] is not None:
			converted = convert(float(record['value']), code)
		else:
			converted = convert(record['value'], code)
		for k, v in converted.iteritems():
			if values.has_key(k):
				values[k].extend([{'date':record['date'], 'value':v}])
			else:
				values.update({k:[{'date':record['date'], 'value':v}]})


	return values






def get_paw_data(widget_data, user):
	raw_values = {}
	params = widget_data['data']['paw']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	avg = params['avg']
	try:
		fc = params['fc']
		wp = params['wp']
		paw_fields = params['pawFields']
	except KeyError:
		print 'KeyError'
	line_color = '#00fff7'
	chart_type = 'line'
	if params.has_key('sensors'):
		sensors = params['sensors']
		if len(sensors) > 1:
			line_color = '#000000'
			try:
				settings = Settings.objects.get(user=user)
				chart_type = settings.calc_graph['paw_avg']
			except (KeyError, Settings.DoesNotExist):
				print 'KeyError or DoesNotExist'
			try:
				settings = Settings.objects.get(user=user)
				line_color = settings.calc_color['paw_avg']
			except (KeyError, Settings.DoesNotExist):
				print 'KeyError or DoesNotExist'

			for i, sensor in enumerate(sensors):
				sens = sensor.split('-')
				if sens[0] == 'fc':
					data_list = load_data(sens[1], sens[2], sens[0], dt_from, dt_to)
					raw_values.update({sensor:{v['date']:v['value'] for i, v in enumerate(data_list)}})
				elif sens[0] == 'dg':
					records = load_data(sens[1], sens[2]+'-'+sens[3], sens[0], dt_from, dt_to)
					data_list = [{
						'date': rec['date'], 
						'value': convert_sca(float(rec['value']), sens[2], 'moist') if rec['value'] is not None else rec['value']} for rec in records]
					raw_values.update({sensor:{v['date']:v['value'] for i, v in enumerate(data_list)}})
		elif len(sensors) == 1:
			try:
				settings = Settings.objects.get(user=user)
				chart_type = settings.calc_graph['paw']
			except (KeyError, Settings.DoesNotExist):
				print 'KeyError or DoesNotExist'
			try:
				settings = Settings.objects.get(user=user)
				line_color = settings.calc_color['paw']
			except (KeyError, Settings.DoesNotExist):
				print 'KeyError or DoesNotExist'

			sens = sensors[0].split('-')
			if sens[0] == 'fc':
				data_list = load_data(sens[1], sens[2], sens[0], dt_from, dt_to)
				raw_values.update({sensors[0]:{v['date']:v['value'] for i, v in enumerate(data_list)}})
			elif sens[0] == 'dg':
				records = load_data(sens[1], sens[2]+'-'+sens[3], sens[0], dt_from, dt_to)
				data_list = [{
					'date': rec['date'], 
					'value': convert_sca(float(rec['value']), sens[2], 'moist') if rec['value'] is not None else rec['value']} for rec in records]
				raw_values.update({sensors[0]:{v['date']:v['value'] for i, v in enumerate(data_list)}})
	else:
		return []
	paw_values = paw(fc, wp, paw_fields, raw_values, avg)
	# alerts = Alert.has_alerts(user, None, 'paw')
	if avg:
		ret_values = [{'date':v['date'], 'value':v['value']} for i, v in enumerate(paw_values)]
		# is sorting neccessary ??
		srtd_values = sorted(ret_values, key=lambda k: k['date'])
		srtd_values[0].update({'lineColor':line_color, 'type':chart_type, 'name':'Average PAW'})
		# watch for alert events
		# for p_avg in srtd_values:
		# 	for a in alerts:
		# 		event = {
		# 			'value': p_avg['value'] if p_avg['value'] is not None else 0,
		# 			'date': p_avg['date'],
		# 			'widget_id': widget_data['id'],
		# 			'sensor': params['sensors']
		# 		}
		# 		alert = Alert.alert_from_model_obj(a)
		# 		alert.watch(event, None, 'paw')
		return [srtd_values]
	else:
		name = 'PAW'
		for lst in paw_values:
			try:
				settings = Settings.objects.get(user=user)
				sens = lst[0]['sensor'].split('-')
				station = Stations.objects.get(user=user, station=sens[1])
				if sens[0] == 'fc':
					name = station.sensors[sens[2]] + ' (PAW)'
				else:
					name = station.sensors[sens[2]+'-'+sens[3]] + ' (PAW)'
				line_color = settings.sensor_color[lst[0]['sensor']]
			except (KeyError, Settings.DoesNotExist, Stations.DoesNotExist):
				print 'KeyError or DoesNotExist'
			lst[0].update({'lineColor':line_color, 'type':chart_type, 'name':name})
			#watch for alert events
			# for p_val in lst:
			# 	for a in alerts:
			# 		event = {
			# 			'value': p_val['value'] if p_val['value'] is not None else 0,
			# 			'date': p_val['date'],
			# 			'widget_id': widget_data['id'],
			# 			'sensor': [lst[0]['sensor']]
			# 		}
			# 		alert = Alert.alert_from_model_obj(a)
			# 		alert.watch(event, None, 'paw')
		return paw_values
	return None




def get_eto_data(widget_data, user):
	print 'calculating eto'
	global DAY
	daily_eto = []
	params = widget_data['data']['evapo']['params'] #(user, db, station, dt_from, dt_to)
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	line_color = ''
	chart_type = ''
	if params.has_key('temp'):
		s_temp = params['temp'].split('-')
		try:
			settings = Settings.objects.get(user=user)
			chart_type = settings.calc_graph['eto']
		except (KeyError, Settings.DoesNotExist):
			print 'KeyError or DoesNotExist'
		try:
			settings = Settings.objects.get(user=user)
			line_color = settings.calc_color['eto']
		except (KeyError, Settings.DoesNotExist):
			print 'KeyError or DoesNotExist'

		if s_temp[0] == 'fc':
			temp_data = load_data(s_temp[1], s_temp[2], s_temp[0], dt_from, dt_to)
			t_min = {v['date']:v['value'] for i, v in enumerate(daily_min(temp_data, 0, 0))}
			t_max = {v['date']:v['value'] for i, v in enumerate(daily_max(temp_data, 0, 0))}
			t_avg = {v['date']:v['value'] for i, v in enumerate(daily_avg(temp_data, 0, 0))}
			s_rh = params['rh'].split('-')
			rh = load_data(s_rh[1], s_rh[2], s_rh[0], dt_from, dt_to)
			rh_min = {v['date']:v['value'] for i, v in enumerate(daily_min(rh, 0, 0))}
			rh_max = {v['date']:v['value'] for i, v in enumerate(daily_max(rh, 0, 0))}
			s_sr = params['sr'].split('-')
			sr = load_data(s_sr[1], s_sr[2], s_sr[0], dt_from, dt_to)
			sr_avg = {v['date']:v['value'] for i, v in enumerate(daily_avg(sr, 0, 0))}
			s_ws = params['ws'].split('-')
			ws = load_data(s_ws[1], s_ws[2], s_ws[0], dt_from, dt_to)
			ws_avg = {v['date']:v['value'] for i, v in enumerate(daily_avg(ws, 0, 0))}
			lat = params['lat']
			alt = params['alt'] #check this 
			start = dt_from
			end = dt_to
			while start <= end:
				start_day = start.strftime('%Y-%m-%d')
				day = dayofyear(start.strftime('%Y-%m-%d %H:%M'))
				if t_min.has_key(start_day) and t_max.has_key(start_day) and\
				t_avg.has_key(start_day) and rh_min.has_key(start_day) and \
				rh_max.has_key(start_day) and sr_avg.has_key(start_day) and ws_avg.has_key(start_day):
					daily_eto.extend([{
						'date':start_day,
						'value':evapotranspiration(sr_avg[start_day], float(alt), t_max[start_day], t_min[start_day], rh_min[start_day], rh_max[start_day], day, float(lat), t_avg[start_day], ws_avg[start_day])}])
				start +=DAY
		elif s_temp[0] == 'dg':
			t_raw = load_data(s_temp[1], s_temp[2]+'-'+s_temp[3], s_temp[0], dt_from, dt_to)
			temp_data = [{
				'date': rec['date'],
				'value': convert_sca(float(rec['value']), s_temp[2], 'temp') if rec['value'] is not None else rec['value']} for rec in t_raw]
			t_min = {v['date']:v['value'] for i, v in enumerate(daily_min(temp_data, 0, 0))}
			t_max = {v['date']:v['value'] for i, v in enumerate(daily_max(temp_data, 0, 0))}
			t_avg = {v['date']:v['value'] for i, v in enumerate(get_d_avg(temp_data, 0, 0, 24))}
			s_rh = params['rh'].split('-')
			rh_raw = load_data(s_rh[1], s_rh[2]+'-'+s_rh[3], s_rh[0], dt_from, dt_to)
			rh = [{'date': rec['date'], 'value': convert_sca(float(rec['value']), s_rh[2], 'rh') if rec['value'] is not None else rec['value']} for rec in rh_raw]
			rh_min = {v['date']:v['value'] for i, v in enumerate(daily_min(rh, 0, 0))}
			rh_max = {v['date']:v['value'] for i, v in enumerate(daily_max(rh, 0, 0))}
			rh_avg = {v['date']:v['value'] for i, v in enumerate(get_d_avg(rh, 0, 0, 24))} # using eq. 19 of FAO doc
			s_sr = params['sr'].split('-')
			sr_raw = load_data(s_sr[1], s_sr[2]+'-'+s_sr[3], s_sr[0], dt_from, dt_to)
			sr = [{'date': rec['date'], 'value': convert_sca(float(rec['value']), s_sr[2], 'sr') if rec['value'] is not None else rec['value']} for rec in sr_raw]
			sr_avg = {v['date']:round(v['value']*0.0864, 3) for i, v in enumerate(get_sum_sr(sr, 0, 0, 24))}
			s_ws = params['ws'].split('-')
			ws_raw = load_data(s_ws[1], s_ws[2]+'-'+s_ws[3], s_ws[0], dt_from, dt_to)
			# print '***********************************', s_ws
			ws = [{'date': rec['date'], 'value': convert_sca(float(rec['value']), s_ws[2], 'speed') if rec['value'] is not None else rec['value']} for rec in ws_raw]
			ws_avg = {v['date']:v['value'] for i, v in enumerate(get_d_avg(ws, 0, 0, 24))}
			lat = params['lat']
			alt = params['alt'] # check this 
			start = dt_from
			end = dt_to
			while start <= end:
				start_day = start.strftime('%Y-%m-%d')
				day = dayofyear(start.strftime('%Y-%m-%d %H:%M'))
				if t_min.has_key(start_day) and t_max.has_key(start_day) and\
				t_avg.has_key(start_day) and rh_min.has_key(start_day) and \
				rh_max.has_key(start_day) and sr_avg.has_key(start_day) and ws_avg.has_key(start_day):
					daily_eto.extend([{
						'date':start_day,
						# 'value':eto_rh_mean(sr_avg[start_day], float(alt), t_max[start_day], t_min[start_day], rh_avg[start_day], day, float(lat), t_avg[start_day], ws_avg[start_day])}])
						'value':evapotranspiration(sr_avg[start_day], float(alt), t_max[start_day], t_min[start_day], rh_min[start_day], rh_max[start_day], day, float(lat), t_avg[start_day], ws_avg[start_day])}])
				start += timedelta(days=1)
	if len(daily_eto) > 0:
		daily_eto[0].update({'lineColor':line_color, 'type':chart_type})
	return daily_eto


def get_dew_point_data(widget_data, user):
	print 'Calculating dew point ...'
	HOUR = timedelta(hours=1)
	daily_dp = []
	params = widget_data['data']['dew_point']['params'] #(user, db, station, dt_from, dt_to)
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	if params.has_key('temp'):
		# print 'has key temp'
		s_temp = params['temp'].split('-')

		line_color = '#000000'
		chart_type = 'line'
		try:
			settings = Settings.objects.get(user=user)
			chart_type = settings.calc_graph['dew_point']
		except (KeyError, Settings.DoesNotExist):
			print 'KeyError or DoesNotExist'
		try:
			settings = Settings.objects.get(user=user)
			line_color = settings.calc_color['dew_point']
		except (KeyError, Settings.DoesNotExist):
			print 'KeyError or DoesNotExist'

		if s_temp[0] == 'fc':
			temp_data = load_data(s_temp[1], s_temp[2], s_temp[0], dt_from, dt_to)
			t_avg = {v['date']:v['value'] for i, v in enumerate(get_hourly_avg(temp_data, 0, 1))}
			s_rh = params['rh'].split('-')
			rh = load_data(s_rh[1], s_rh[2], s_rh[0], dt_from, dt_to)
			rh_avg = {v['date']:v['value'] for i, v in enumerate(get_hourly_avg(rh, 0, 1))}
			start = dt_from.replace(second=0, microsecond=0)
			end = dt_to.replace(second=0, microsecond=0)
			while start <= end:
				start_day = date_to_string(start)
				if t_avg.has_key(start_day) and rh_avg.has_key(start_day):
					daily_dp.extend([{'date':start_day, 'value':dew_point(t_avg[start_day], rh_avg[start_day])}])
				start +=HOUR
		elif s_temp[0] == 'dg':
			t_raw = load_data(s_temp[1], s_temp[2]+'-'+s_temp[3], s_temp[0], dt_from, dt_to)
			temp_data = [{'date':rec['date'], 'value':convert_sca(float(rec['value']), s_temp[2], 'temp') if rec['value'] is not None else rec['value']} for rec in t_raw]
			t_avg = {v['date']:v['value'] for i, v in enumerate(get_hourly_avg(temp_data, 0, 1))}
			s_rh = params['rh'].split('-')
			rh_raw = load_data(s_rh[1], s_rh[2]+'-'+s_rh[3], s_rh[0], dt_from, dt_to)
			rh = [{'date':rec['date'], 'value':convert_sca(float(rec['value']), s_rh[2], 'rh')  if rec['value'] is not None else rec['value']} for rec in rh_raw]
			rh_avg = {v['date']:v['value'] for i, v in enumerate(get_hourly_avg(rh, 0, 1))}
			start = dt_from.replace(second=0, microsecond=0)
			end = dt_to.replace(second=0, microsecond=0)
			while start <= end:
				start_day = date_to_string(start)
				if t_avg.has_key(start_day) and rh_avg.has_key(start_day):
					daily_dp.extend([{'date':start_day, 'value':dew_point(t_avg[start_day], rh_avg[start_day])}])
				start +=HOUR
	print 'daily_dp returning'
	# try:
	daily_dp[0].update({'lineColor':line_color, 'type':chart_type})
	# except IndexError as e:
	# 	print e
	return daily_dp


def get_cportions_data(widget_data, user):
	print 'Calculating chilling portions '
	daily_chip = []
	params = widget_data['data']['chilling_portions']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	RESET_DATE = '01-01' +' '+ '08:00'
	YEAR = str(dt_from.year)
	chart_type = 'column'
	line_color = '#00fff7'
	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.cportions['cp_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'

	dt_reset = parse_date(YEAR+'-'+RESET_DATE)

	#set dt_from to previous year
	if dt_from < dt_reset:
		YEAR = str(int(YEAR) - 1)
		dt_reset = parse_date(YEAR+'-'+RESET_DATE)	

	if not params.has_key('sensors'):
		return []

	s_temp = params['sensors'].split('-')

	try:
		settings = Settings.objects.get(user=user)
		chart_type = settings.calc_graph['chilling_portions']
	except (KeyError, Settings.DoesNotExist):
		print 'KeyError or DoesNotExist'
	try:
		settings = Settings.objects.get(user=user)
		line_color = settings.calc_color['chilling_portions']
	except (KeyError, Settings.DoesNotExist):
		print 'KeyError or DoesNotExist'

	if s_temp[0] == 'fc':
		print 'Retrieving fieldclimate data from local database...'
		entries = StationData.objects.filter(station_id=s_temp[1], database=s_temp[0])
		if not entries.exists():
			print 'No data found in the local database.'
			return []
		raw_data = load_data(s_temp[1], s_temp[2], s_temp[0], dt_reset, dt_to)
		cportions = calculate_cportions(get_hourly_avg(raw_data, 0, 1), RESET_DATE)
		cp_data = [{'date':portions['date'], 'value':portions['accumulation']} for portions in cportions if dt_from <= parse_date(portions['date']) <= dt_to]
		cp_data[0].update({'lineColor':line_color, 'type':chart_type})
		return cp_data

	elif s_temp[0] == 'dg':
		print 'Retrieving decagon data from local database...'
		entries = StationData.objects.filter(station_id=s_temp[1], database=s_temp[0])
		if not entries.exists():
			print 'No data found in the local database.'
			return []
		data = load_data(s_temp[1], s_temp[2]+'-'+s_temp[3], s_temp[0], dt_reset, dt_to)
		raw_data = [{
			'date': rec['date'],
			'value': convert_sca(float(rec['value']), s_temp[2], 'temp')  if rec['value'] is not None else rec['value']} for rec in data] 
		cportions = calculate_cportions(raw_data, RESET_DATE)
		cp_data = [{'date':portions['date'], 'value':portions['accumulation']} for portions in cportions if dt_from <= parse_date_s(portions['date']) <= dt_to]
		cp_data[0].update({'lineColor':line_color, 'type':chart_type})
		return cp_data
	return False

def calculate_cportions(raw_data, RESET_DATE):
	cportions = []
	prev_portions = {'xi':0.0, 'inter_e':0.0, 'delt':0.0, 'portions':0.0, 'accumulation':0.0}	
	# print raw_data
	for data in raw_data:
		# if parse_date(data['date']).minute != 0:
		# 	continue
		if parse_date(data['date']).month == int(RESET_DATE.split('-')[0]) and parse_date(data['date']).day == 1 and parse_date(data['date']).hour == 8:
			prev_portions = {'xi':0.0, 'inter_e':0.0, 'delt':0.0, 'portions':0.0, 'accumulation':0.0}
		value = float(data['value']) if data['value'] is not None else 0
		portions = chill_portions(value, prev_portions)
		portions.update({'date': data['date']})
		# print portions
		cportions.extend([portions])
		prev_portions = portions
	return cportions

def get_chill_hours_data(widget_data, user):
	params = widget_data['data']['chilling_hours']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	threshold = params['th']
	RESET_DATE = '01-01' +' '+ '08:00'
	YEAR = str(dt_from.year)

	if not params.has_key('sensors'):
		return False
	s_temp = params['sensors'].split('-')

	line_color = '#000000'
	chart_type = 'line'
	if threshold == '':
		try:
			settings = Settings.objects.get(user=user)
			threshold = int(settings.chours['ch_threshold'])
		except (KeyError, Settings.DoesNotExist):
			print 'KeyError or DoesNotExist'
			threshold = 7
	else:
		threshold = int(threshold)

	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.chours['ch_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'
	
	dt_reset = parse_date(YEAR+'-'+RESET_DATE)

	#set dt_from to that of previous year
	if dt_from < dt_reset:
		YEAR = str(int(YEAR) - 1)
		dt_reset = parse_date(YEAR+'-'+RESET_DATE)	

	try:
		settings = Settings.objects.get(user=user)
		chart_type = settings.calc_graph['chilling_hours']
	except (KeyError, Settings.DoesNotExist):
		print 'KeyError or DoesNotExist'
	try:
		settings = Settings.objects.get(user=user)
		line_color = settings.calc_color['chilling_hours']
	except (KeyError, Settings.DoesNotExist):
		print 'KeyError or DoesNotExist'
	# print RESET_DATE
	# print threshold
	if s_temp[0] == 'fc':
		print 'Retrieving fieldclimate data from local database...'
		entries = StationData.objects.filter(station_id=s_temp[1], database=s_temp[0])
		if not entries.exists():
			print 'No data found in the local database.'
			return []
		raw_data = load_data(s_temp[1], s_temp[2], s_temp[0], dt_reset, dt_to)
		chill_hours_acc = calculate_chill_hours(raw_data, threshold, RESET_DATE)
		ch_data = [{'date': hours['date'], 'value':hours['value']} for hours in chill_hours_acc if dt_from <= parse_date(hours['date']) <= dt_to]
		ch_data[0].update({'lineColor': line_color, 'type':chart_type})
		return ch_data
	elif s_temp[0] == 'dg':
		print 'Retrieving decagon data for chiling hours calculation from local database...'
		entries = StationData.objects.filter(station_id=s_temp[1], database=s_temp[0])
		if not entries.exists():
			print 'No data found in the local database.'
			return []
		data = load_data(s_temp[1], s_temp[2]+'-'+s_temp[3], s_temp[0], dt_reset, dt_to)
		raw_data = [{
			'date': rec['date'],
			'value': convert_sca(float(rec['value']), s_temp[2], 'temp') if rec['value'] is not None else rec['value']} for rec in data] 
		chill_hours_acc = calculate_chill_hours(raw_data, threshold, RESET_DATE)
		ch_data = [{'date': hours['date'], 'value':hours['value']} for hours in chill_hours_acc if dt_from <= parse_date(hours['date']) <= dt_to]
		ch_data[0].update({'lineColor': line_color, 'type':chart_type})
		return ch_data
	return False


def calculate_chill_hours(raw_data, threshold, RESET_DATE):
	chill_hours_acc = []
	date1 = parse_date(raw_data[0]['date'])
	accumulation = 0
	count = 0
	hour_sum = 0
	reset = False
	for data in raw_data:
		if parse_date(data['date']).month == int(RESET_DATE.split('-')[0]) and parse_date(data['date']).day == 1 and parse_date(data['date']).hour == 8:
			reset = True
		if (parse_date(data['date']) - date1) < HOUR:
			hour_sum += float(data['value']) if data['value'] is not None else 0
			count +=1
		else:
			if count == 0:
				value = float(data['value']) if data['value'] is not None else data['value']
				if chill_hours(value, threshold):
					accumulation+=1
			else:
				if chill_hours(hour_sum/count, threshold):
					accumulation+=1
			if reset:
				accumulation = 0
				reset = False
			chill_hours_acc.extend([{'date': data['date'], 'value':accumulation}])
			hour_sum = 0
			count = 0
			date1 = parse_date(data['date'])

	return chill_hours_acc


def get_degree_days_data(widget_data, user):
	params = widget_data['data']['degree_days']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	threshold = params['th']
	line_color = '#000000'
	chart_type = 'line'
	RESET_DATE = '01-01' +' '+ '08:00'
	YEAR = str(dt_from.year)
	if not params.has_key('sensors'):
		return False
	print 'has key sensors: True'
	s_temp = params['sensors'].split('-')

	if threshold == '':
		try:
			settings = Settings.objects.get(user=user)
			threshold = int(settings.ddays['dd_threshold'])
		except (KeyError, Settings.DoesNotExist):
			print 'KeyError or DoesNotExist'
			threshold = 10
	else:
		threshold = int(threshold)

	try:
		settings = Settings.objects.get(user=user)
		RESET_DATE = settings.ddays['dd_reset_dt'] + '-01 08:00'
	except (KeyError, Settings.DoesNotExist):
		print ' KeyError or Settings.DoesNotExist'

	dt_reset = parse_date(YEAR+'-'+RESET_DATE)

	#set dt_from to that of previous year
	if dt_from < dt_reset:
		YEAR = str(int(YEAR) - 1)
		dt_reset = parse_date(YEAR+'-'+RESET_DATE)	
	
	try:
		settings = Settings.objects.get(user=user)
		chart_type = settings.calc_graph['degree_days']
	except (KeyError, Settings.DoesNotExist):
		print 'KeyError or DoesNotExist'
	try:
		settings = Settings.objects.get(user=user)
		line_color = settings.calc_color['degree_days']
	except (KeyError, Settings.DoesNotExist):
		print 'KeyError or DoesNotExist'

	if s_temp[0] == 'fc':
		print 'Retrieving fieldclimate data for degree days calculation from local database...'
		entries = StationData.objects.filter(station_id=s_temp[1], database=s_temp[0])
		if not entries.exists():
			print 'No data found in the local database.'
			return []
		
		raw_data = load_data(s_temp[1], s_temp[2], s_temp[0], dt_reset, dt_to)
		print RESET_DATE
		daily_avg = get_daily_avg(raw_data)
		degree_days_acc = calculate_degree_days(daily_avg, threshold, RESET_DATE)
		dd_data = [{
			'date': degrees['date'],
			'value':degrees['value']} for degrees in degree_days_acc if dt_from <= parse_date_d(degrees['date']) <= dt_to]
		dd_data[0].update({'lineColor': line_color, 'type':chart_type})
		return dd_data
	elif s_temp[0] == 'dg':
		print 'Retrieving decagon data for degree days calculation from local database...'
		entries = StationData.objects.filter(station_id=s_temp[1], database=s_temp[0])
		if not entries.exists():
			print 'No data found in the local database.'
			return []
		data = load_data(s_temp[1], s_temp[2]+'-'+s_temp[3], s_temp[0], dt_reset, dt_to)
		raw_data = [{
			'date': rec['date'],
			'value': convert_sca(float(rec['value']), s_temp[2], 'temp') if rec['value'] is not None else rec['value']} for rec in data] 
		daily_avg = get_daily_avg(raw_data)
		degree_days_acc = calculate_degree_days(daily_avg, threshold, RESET_DATE)
		dd_data = [{'date': degrees['date'], 'value':degrees['value']} for degrees in degree_days_acc if dt_from <= parse_date_d(degrees['date']) <= dt_to]
		dd_data[0].update({'lineColor': line_color, 'type':chart_type})
		return dd_data

	return False


def calculate_degree_days(raw_data, threshold, RESET_DATE):
	degree_days_acc = []
	accumulation = 0
	for data in raw_data:
		if parse_date_d(data['date']).month == int(RESET_DATE.split('-')[0]) and parse_date_d(data['date']).day == 1:
			accumulation = 0
		value = float(data['value']) if data['value'] is not None else 0
		accumulation += degree_days(value, threshold)
		degree_days_acc.extend([{'date': data['date'], 'value':accumulation}])
	return degree_days_acc

def get_sat_ec_data(widget_data, user):
	graphs = widget_data['data']['ex_ec']['params']['sensors']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	avg = widget_data['data']['ex_ec']['params']['avg']
	sat_ex_ec_data = []
	if len(graphs) == 0:
		return []
	for graph in graphs:
		if len(graph['sensors']) == 0:
			return []
		offset = float(graph['offset'])
		saturation = float(graph['saturation'])
		if len(graph['sensors']) == 1:
			sens = graph['sensors'][0].split('-')
			if sens[0] != 'dg':
				return []
			raw_data = load_data(sens[1], sens[2]+'-'+sens[3], sens[0], dt_from, dt_to)
			if len(raw_data) == 0:
				return []
			if sens[2] not in ['119', '122']:
				return []
			ex_ec_data = []
			for data in raw_data:
				vwc = convert_sca(data['value'], sens[2], 'moist') if data['value'] is not None else data['value']
				perm = convert_sca(data['value'], sens[2], 'perm') if data['value'] is not None else data['value']
				temp = convert_sca(data['value'], sens[2], 'temp') if data['value'] is not None else data['value']
				ec = convert_sca(data['value'], sens[2], 'ec') if data['value'] is not None else data['value']
				ex_ec_data.extend([{'date':data['date'], 'value': saturation_ec(temp, vwc, ec, perm, offset, saturation, 'mscm')}])
			ex_ec_data[0].update({'sensor': 'sat_ex_ec', 'name': graph['label']})
			sat_ex_ec_data.extend([ex_ec_data])
		elif len(graph['sensors']) > 1:
			sensors = graph['sensors']
			sens_vwc = ''
			sens_temp = ''
			sens_ec = ''
			sens_perm = ''
			for sensor in sensors:
				if sensor.split('-')[0] != 'fc':
					return []
				if sensor.split('_')[-2] == '30738':
					sens_ec = sensor
				elif sensor.split('_')[-2] == '30737':
					sens_perm = sensor
				elif sensor.split('_')[-2] == '34674':
					sens_temp = sensor
				elif sensor.split('_')[-2] == '30739':
					sens_vwc = sensor
			if sens_vwc ==  '' or sens_temp == '' or sens_ec == '' or sens_perm == '':
				return []
			ec_data = load_data(sens_ec.split('-')[1], sens_ec.split('-')[2], sens_ec.split('-')[0], dt_from, dt_to)
			vwc_data = load_data(sens_vwc.split('-')[1], sens_vwc.split('-')[2], sens_vwc.split('-')[0], dt_from, dt_to)
			temp_data = load_data(sens_temp.split('-')[1], sens_temp.split('-')[2], sens_temp.split('-')[0], dt_from, dt_to)
			perm_data = load_data(sens_perm.split('-')[1], sens_perm.split('-')[2], sens_perm.split('-')[0], dt_from, dt_to)

			ex_ec_data = calculate_sat_ec_fc(ec_data, vwc_data, temp_data, perm_data, offset, saturation, 'dsm')
			ex_ec_data[0].update({'sensor': 'sat_ex_ec', 'name': graph['label']})
			sat_ex_ec_data.extend([ex_ec_data])

		elif len(graph['sensors']) > 4:
			return []
	return sat_ex_ec_data


def calculate_sat_ec_fc(ec, vwc, temp, perm, offset, saturation, unit):
	ex_ec_data = []
	if len(ec) == len(vwc) == len(temp) == len(perm):
		for i in range(0, len(temp)):
			ex_ec_data.extend([{
				'date':temp[i]['date'],
				'value':saturation_ec(temp[i]['value'], vwc[i]['value'], ec[i]['value'], perm[i]['value'], offset, saturation, unit)}])
	else:
		for i in range(0, min(len(ec), len(vwc), len(temp), len(perm))):
			ex_ec_data.extend([{
				'date':temp[i]['date'],
				'value':saturation_ec(temp[i]['value'], vwc[i]['value'], ec[i]['value'], perm[i]['value'], offset, saturation, unit)}])
	return ex_ec_data	


def get_voltage_data(widget, user):
	from Equation import Expression
	graphs = widget['data']['voltage']['params']['sensors']
	dt_from = parse_date(widget['data']['range']['from'])
	dt_to = parse_date(widget['data']['range']['to'])
	result = []
	if len(graphs) == 0:
		return []	
	for graph in graphs:
		voltage_data = []
		if len(graph['sensor']) == 0:
			continue
		equation = graph['equation']
		sensor = graph['sensor'][0].split('-')
		if sensor[0] == 'fc':
			raw_data = load_data(sensor[1], sensor[2], sensor[0], dt_from, dt_to)
		else:
			raw_data = load_data(sensor[1], sensor[2]+'-'+sensor[3], sensor[0], dt_from, dt_to)
			#222: LWS Leaf Wetness Sensor, 183: Flow Meter Sensor, 221: PS-1 Pressure Switch
			#189: ECRN-50.Perc.[mm]
			if sensor[2] in ['222', '180', '221', '189']:
				accum_data = get_hourly_sum(raw_data, 1)
				raw_data = accum_data
			#187: ECRN-100.Perc.[mm]
			if sensor[2] in ['187']:
				accum_data = get_hourly_sum(raw_data, 0.2)
				raw_data = accum_data
			#188: ECRN-50.Perc.vol.[ml]
			if sensor[2] in ['188']:
				accum_data = get_hourly_sum(raw_data, 5)
				raw_data = accum_data
			if sensor[2] in ['183']:
				accum_data = get_quarterly_sum(raw_data, 1)
				raw_data = accum_data
	# vwc = convert_sca(data['value'], sens[2], 'moist') if data['value'] is not None else data['value']
		if len(raw_data) < 1:
			continue
		for data in raw_data:
			value = None
			date = data['date']
			if sensor[0] == 'fc':
				value = float(data['value'])
			else:
				value = convert_sca(data['value'], sensor[2], '') if data['value'] is not None else None
			if value is None:
				voltage_data.extend([{'date': date, 'value': value}])
				continue
			try:
				fn = Expression(equation, ['x'])
				s_value = fn(value)
			except Exception as e:
				print e
				voltage_data.extend([{'date': date, 'value': None}])
			voltage_data.extend([{'date': date, 'value': s_value}])
			# print voltage_data
		if len(voltage_data) > 1:
			voltage_data[0].update({'sensor':'', 'name':graph['label']})
			result.extend([voltage_data])
	return result

def load_data(station_id, sensor, database, dt_from, dt_to):
	diff = dt_to - dt_from
	records = StationData.objects.filter(station_id=station_id, database=database, date__range=(dt_from, dt_to)).values('data')
	if not records.exists():
		if database == 'fc':
			get_data_fc(station_id)
		elif database == 'dg':
			get_data_dg(station_id)
		return [] # fix this shit ------------------
	
	max_entry = parse_date(json.loads(records.last()['data'])['date'])

	# print max_entry
	# print sensor
	if max_entry < dt_to:
		dt_to = max_entry
		dt_from = dt_to - diff

	data = []	
	for rec in records:
		# print rec
		try:
			data.extend([{
				'date':json.loads(rec['data'])['date'],
				'value':json.loads(rec['data'])[sensor]}])
		except KeyError as e:
			print e
			data.extend([{
				'date':json.loads(rec['data'])['date'],
				'value':None}])

	return data

def load_widgets(user):
	# print 'load widget in get_records called'
	# data_dict = {'degree_days_acc': 'Degree Days Accu.', 'temp_min':'Min Temperature', 'temp_avg':'Avg. Temperature',
	#  'temp_max': 'Max Temperature', 'chilling_hours_acc':'Chilling Hours Accu.'}
	try:
		active_dashboard = Dashboard.objects.get(user=user, active=True)
	except Exception, e:
		raise e
	widget_dict = {}
	widgets = Widgets.objects.filter(user=user, dashboard=active_dashboard)
	if widgets.exists():
		for widget in widgets:
			if widget.widget_type != 'stat':
				widget_dict.update({
					widget.widget['id']:{
						'widget':widget.widget,
						# 'w_json':json.dumps(widget.widget),
						# 'sensor':data_dict[widget.widget['data']['calc']['params']['sensor']]
						}
						})
	return widget_dict




def set_password(self, raw_password):
	self.fc_salt = uuid.uuid4().hex
	self.fc_password = hashlib.sha512(fc_password + salt).hexdigest()



def user_settings(user):
	sensor_recs = SensorCodes.objects.filter(user=user)
	info_dict = {'sensor_info':{}}
	for rec in sensor_recs:
		info = {rec.sensor_id:{'code':rec.sensor_id, 'name':rec.sensor_name, 'unit':rec.sensor_unit}}
		info_dict['sensor_info'].update(info)
	return info_dict
	

# def add_fc_station(user, data):
# 	print 'adding station'

# 	try:
# 		fc_acc = AppUser.objects.get(user=user)
# 		response = requests.post("http://www.fieldclimate.com/api/CIDIUser/AddStation",
# 			data={"user_name": fc_acc.fc_username, "user_passw" : fc_acc.fc_password,\
# 			 "station_name": data['station_id'],"station_key":data['password'], "user_station_name":data['alias']})
# 	except requests.exceptions.RequestException as e:
# 		print e
# 		return add_fc_station(user, data)
# 	print 'response received'
# 	if response.status_code == 200:
# 		print '200'
# 		res = json.loads(response.text)
# 		if res.has_key('faultcode'):
# 			data['success'] = False
# 			data['message'] = res['faultstring']
# 			return data
# 		elif res.has_key('ReturnDataSet'):
# 			if res['ReturnDataSet'] == "station_added":
# 				print ' success adding station'
# 				success = download_station_data(data['station_id'], 'fc', user)
# 				data['success'] = success
# 				if success:
# 					update_fc_stations(user, data['station_id'], data['password'])
# 					data['message'] = 'Station successfully added. Please refresh page.'
# 				else:
# 					data['message'] = 'Problem downloading station data. Please try again.'
# 				return data
# 	else:
# 		data['success'] = False
# 		data['message'] = 'Problem adding station. Please try again.'
# 		return data


def add_fc_station(user, data):

	MAX_RETRY = 3
	path = '/station/'+data['station_id']+'/'+data['password']
	print path
	headers = make_headers('POST', path)
	url = 'https://api.fieldclimate.com'
	schema = json.dumps({"custom_name": data['alias']})

	while MAX_RETRY > 1:
		MAX_RETRY -= 1
		try:
			response = requests.post(url + path, headers=headers, data=schema, verify=False) # very=false: this needs to be fixed
		except requests.exceptions.RequestException as e:
			print e 
			print 'Retrying in 3 seconds...'
			time.sleep(3)
			continue
		if response.status_code != 200:
			print 'Server returned http ', response.status_code
			# print response.text
			if response.status_code == 409:
				station = Stations.objects.filter(station=data['station_id'])
				if station.exists():
					if station.filter(user=user).exists():
						data['success'] = True
						data['message'] = 'Station already exists.'
						return data
					elif station.filter(code=data['password']).exists():
						try:
							new_station = Stations(user=user, station=station[0].station, name=data['alias'], database='fc', code=station[0].code,\
								sensors=station[0].sensors, inactive_sensors=station[0].inactive_sensors)
							new_station.save()
						except (ValueError, IntegrityError) as e:
							print e
							data['success'] = False
							data['message'] = 'Invalid parameters.'
							return data
						data['success'] = True
						data['message'] = 'Station added successfully.'
						return data
					else:
						#can be verified by trying to download data
						authenticated = get_data_fc(data['station_id'])
						if authenticated:
							try:
								new_station = Stations(user=user, station=data['station_id'], name=data['alias'], database='fc', code=data['password'],\
									sensors={}, inactive_sensors={})
								new_station.save()
							except (ValueError, IntegrityError) as e:
								print e
								data['success'] = False
								data['message'] = 'Invalid parameters.'
								return data
							sensors = update_sensor_lst(new_station.station)
							data['success'] = True
							data['message'] = 'Station added successfully.'
							if sensors is None:
								data['message'] += ' Sensors list not updated!'
							if not data_download:
								data['message'] += ' Station data download failed!'
							return data
						else:
							data['success'] = False
							data['message'] = 'Station cannot be authenticated.'
							return data
				else:
					#can be verified by trying to download data
					authenticated = get_data_fc(data['station_id'])
					if authenticated:
						try:
							new_station = Stations(user=user, station=data['station_id'], name=data['alias'], database='fc', code=data['password'],\
								sensors={}, inactive_sensors={})
							new_station.save()
						except (ValueError, IntegrityError) as e:
							print e
							data['success'] = False
							data['message'] = 'Invalid parameters.'
							return data
						sensors = update_sensor_lst(data['station_id'])
						data['success'] = True
						data['message'] = 'Station added successfully.'
						if sensors is None:
							data['message'] += ' Sensors list not updated!'
						# if not data_download:
# 							data['message'] += ' Station data download failed!'
						return data
					else:
						data['success'] = False
						data['message'] = 'Station cannot be authenticated.'
						return data
			print 'Retrying in 3 seconds...'
			time.sleep(3)
			continue
		else:
			print 'station successfully added.', json.loads(response.text)
			return json.loads(response.text)
			station = Stations.objects.filter(station=data['station_id'])
			if station.exists():
				if station.filter(user=user).exists():
					data['success'] = True
					data['message'] = 'Station ready.'
					return data
				else:
					try:
						new_station = Stations(user=user, station=station[0].station, name=data['alias'], database='fc', code=station[0].code,\
							sensors=station[0].sensors, inactive_sensors=station[0].inactive_sensors)
						new_station.save()
					except (ValueError, IntegrityError) as e:
						print e
						data['success'] = False
						data['message'] = 'Invalid parameters.'
						return data
					data['success'] = True
					data['message'] = 'Station added successfully.'
					return data
			else:
				try:
					new_station = Stations(user=user, station=data['station_id'], name=data['alias'], database='fc', code=data['password'],\
						sensors={}, inactive_sensors={})
					new_station.save()
				except (ValueError, IntegrityError) as e:
					print e
					data['success'] = False
					data['message'] = 'Invalid parameters.'
					return data
				sensors = update_sensor_lst(new_station.station)
				data_download = get_data_fc(new_station.station)
				data['success'] = True
				data['message'] = 'Station added successfully.'
				if sensors is None:
					data['message'] += ' Sensors list not updated!'
				if not data_download:
					data['message'] += ' Station data download failed!'
				return data

	data['success'] = False
	data['message'] = 'Failed to add station.'
	return data


def add_dg_station(user, data):
	print 'Adding decagon station ...'

	if Stations.objects.filter(user=user, station=data['station_id']).exists():
		data['success'] = False
		data['message'] = 'Station already exists.'
		return data

	try:
		dg_acc = AppUser.objects.get(user=user)
		params = {
			'email': dg_acc.dg_username,
		 	'userpass': dg_acc.dg_password,
		 	'deviceid': data['station_id'],
		 	'devicepass': data['password'],
		 	'report': 0,
		 	'User-Agent': 'AgViewer_1.0'
		 	}
		url = 'http://api.ech2odata.com/morph2ola/dxd.cgi'
		response = requests.post(url, data=params)
	except requests.exceptions.RequestException as e:
		print e

	if response.status_code == 200:
		success = get_data_decagon(data['station_id'], user, data['password'])
		print 'success: ', success
		data['success'] = success
		if success:
			data['message'] = 'Station successfully added. Please refresh page.'
		else:
			data['message'] = 'Problem downloading station data. Please try again.'
		return data
	else:
		data['success'] = False
		data['message'] = 'Error adding station. Please retry. Decagon: ' + str(response.status_code) 
		return data


def list_files(user):
	files = Files.objects.filter(user=user)
	if files.exists():
		file_lst = [file.file.name for file in files if file.file.name.split('.')[-2] != 'kmz'] #list only files with .kmz or .kml extension
		return file_lst
	return []

def get_data_decagon(device, user, devicepass):
	# from datetime import datetime
	print 'downloading decagon data...'
	mrid = 0
	prev_records = StationData.objects.filter(station_id=device)
	dg_acc = AppUser.objects.get(user=user)
	if prev_records.exists():
		mrid = prev_records.last().mrid
		params = {
			'email': dg_acc.dg_username,
			'userpass': dg_acc.dg_password,
			'deviceid': device,
			'devicepass': devicepass,
			'report': 1,
			'mrid': mrid,
			'User-Agent': 'AgViewer_1.0'
		}
	else:
		# 3 months ago in linux epoch seconds
		time = int(((datetime.now() - timedelta(days=90)) - datetime(1970,1,1)).total_seconds())
		params = {
			'email': dg_acc.dg_username,
			'userpass': dg_acc.dg_password,
			'deviceid': device,
			'devicepass': devicepass,
			'report': 1,
			'time': time,
			'User-Agent': 'AgViewer_1.0'
		}

	try:
		
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
			if not Stations.objects.filter(user=user, station=device).exists():
				station_info = station_from_xml(response.text)
				station = Stations(user=user, station=station_info['station'], name=station_info['name'], database='dg', code=devicepass, sensors=station_info['sensors'])
				station.save()
	except requests.exceptions.RequestException as e:
		print e
	
	
	return True

def download_station_data(station, database, user):
	print 'first time download started.'
	if database == 'fc':
		success = get_data_fc(station)
		return success
	elif database == 'dg':
		success = get_data_dg(station)
		return success
	return False
		
def update_fc_stations(user, station, code): # edit 1 for new sensors code
	print 'updating stations ...'
	appuser = AppUser.objects.get(user=user)

	sensor_codes =[sensor.sensor_id for sensor in SensorCodes.objects.all()]
	sensors = {}
	defaults = {}
	minmax = ['min', 'max', 'aver']
	if not Stations.objects.filter(user=user, station=station).exists():
		try:
			response1 = requests.post("http://fieldclimate.com/api/index.php?action=CIDIStationData_GetLast",
				data={
					"user_name": appuser.fc_username,
				 	"user_passw" : appuser.fc_password,
				 	"station_name": station,
				 	"row_count": 1
				 	})
		except requests.exceptions.RequestException as e:
			print e 
			return False
		print 'response1 returned: ', response1.status_code
		for sensor in json.loads(response1.text)['ReturnDataSet'][0]:
			print 'looping through senosrs'
			if sensor == 'f_date' or sensor == 'f_log_int':
				continue
			if sensor.split('_')[len(sensor.split('_'))-2] in sensor_codes:
				print 'sensor in SensorCodes'
				sensor_name = SensorCodes.objects.get(sensor_id=sensor.split('_')[len(sensor.split('_'))-2]).sensor_name and SensorCodes.objects.get(sensor_id=sensor.split('_')[len(sensor.split('_'))-2]).sensor_name or sensor
				if sensor.split('_')[1] in minmax:
					sensor_name = sensor_name+' ['+sensor.split('_')[len(sensor.split('_'))-2]+' '+sensor.split('_')[1]+']'
				else:
					sensor_name = sensor_name+' ['+sensor.split('_')[len(sensor.split('_'))-2]+']'
				sensors.update({sensor:sensor_name})
			else:
				print 'getting sensor list from FC'
				try:
					url2 = "http://fieldclimate.com/api/CIDIStationSensors/Get"
					data2 = {
						'user_name':appuser.fc_username,
						'user_passw':appuser.fc_password,
						'station_name': station
						}
					response2 = requests.post(url2, data2)
				except requests.exceptions.RequestException as e:
					print e

				print 'response2 returned: ', response2.status_code
				for rec in json.loads(response2.text)['ReturnDataSet']:
					if rec['f_sensor_code'] == sensor:
						if sensor.split('_')[1] in minmax:
							sensor_name = rec['f_name']+' ['+sensor.split('_')[len(sensor.split('_'))-2]+' '+sensor.split('_')[1]+']'
						else:
							sensor_name = rec['f_name']+' ['+sensor.split('_')[len(sensor.split('_'))-2]+']'
						if rec['f_name'] == '':
							sensor_name = sensor
						sensors.update({sensor:sensor_name})
						defaults.update({'sensor_name':sensor_name, 'sensor_unit':rec['f_unit_code']})
						break
					else:
						pass
				# if not sensor in sensors:
				# 	sensors.update({sensor:'Untitled'})
				# 	defaults.update({'sensor_name':'Untitled', 'sensor_unit':'XX', 'user':user})
				SensorCodes.objects.get_or_create(user=user,sensor_id=sensor.split('_')[len(sensor.split('_'))-2], defaults=defaults)
		station = Stations(user=user, station=station, name=station, database='fc', code=code, sensors=sensors)
		station.save()
	return True

def get_unit(user, station, sensor):
	unit = ''
	print 'error here 1'
	try:
		sensor = Units.objects.get(user=user, sensor_id=sensor)
		return sensor.sensor_unit
		print 'error here 2'
	except Units.DoesNotExist:
		print 'Unit DoesNotExist.'
	try:
		appuser = AppUser.objects.get(user=user)
		url = "http://fieldclimate.com/api/CIDIStationSensors/Get"
		data = {
			'user_name':appuser.fc_username,
			'user_passw':appuser.fc_password,
			'station_name': station
			}
		response = requests.post(url, data)
	except requests.exceptions.RequestException as e:
		print e

	try:
		sensors_info = json.loads(response)['ReturnDataSet']
		for item in sensors_info:
			sensor_obj = Units(user=user, sensor_id=sensor, sensor_unit=item['f_unit'])
			sensor_obj.save()
			if item['f_sensor_code'] == sensor:
				unit = item['f_unit']
		return unit
		print unit
	except KeyError:
		raise e

