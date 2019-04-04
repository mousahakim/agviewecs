import json, requests, time, simplejson
from django.http import HttpResponse
from models import *
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from visualizer.calculations import *
from visualizer.decagon import dayofyear
import datetime, time
from datetime import timedelta
from django.utils import timezone
from visualizer.utils import *
import pprint

# globals
DAY = datetime.timedelta(days=1)
HOUR = datetime.timedelta(hours=1)



def set_station_list(user): # AppUser object passed as parameter

	response = requests.post("http://www.fieldclimate.com/api/index.php?action=CIDIStationList_GetStations",
	data={"user_name": user.fc_username, "user_passw" : user.fc_password}) 
	res = json.loads(response.text)

	station_dict = {}
	for k, v in res['ReturnDataSet'].iteritems():
		station_dict.update({k:v['custom_name']})

	for obj in StationList.objects.all():
		if obj.user == user.user:
			obj.station_list = json.dumps(station_dict)
			return

	station_list = StationList(user=user.user, station_list=json.dumps(station_dict))
	station_list.save()


def get_station_list(user): # pass appuser object

	for obj in StationList.objects.all():
		if obj.user == user.user:
			return obj.station_list

	set_station_list(user)
	return get_station_list(user)


def set_sensor_list(user, station_name):
	url ="http://www.fieldclimate.com/api/index.php?action=CIDIStationSensors_Get"
	response = requests.post(url, data={"user_name": user.fc_username, "user_passw" : user.fc_password, "station_name": station_name})
	res = json.loads(response.text)
	sensor_dict = {}
	for r in res['ReturnDataSet']:
		sensor_dict.update({r['f_sensor_code']:r['f_sensor_user_name']})

	for obj in SensorList.objects.all():
		if obj.station == station_name:
			obj.sensor_list = json.dumps(sensor_dict)
			print obj.sensor_list
			return
	# print sensor_dict['0']
	sensor_list = SensorList(station=station_name, sensor_list=json.dumps(sensor_dict))
	sensor_list.save()


def get_sensor_list(user, station_name):
	for obj in SensorList.objects.all():
		if obj.station == station_name:
			return obj.sensor_list

	set_sensor_list(user, station_name)
	return get_sensor_list(user, station_name)


def get_station_sensor_list(user):

	station_sensor_dict = {}

	station_dict = json.loads(StationList.objects.get(user=user.user).station_list)

	for k, v in station_dict.iteritems():
		if SensorList.objects.filter(station=k).exists():
			station_sensor_dict.update({v:SensorList.objects.get(station=k).sensor_list})

	return station_sensor_dict

def get_vwc_sensors(user):
	
	vwc = {'fc':'', 'dg':''}
	vwc_dict_dg = {}

	soil_moist_codes = ['24321', '19201', '19969', '19953', '25857', '26881', '36097', '20227', '34689', '36100']
	soil_moist_codes_dg = ['253', '254', '252','249', '125', '127', '122', '120', '119']
	station_obj = StationList.objects.filter(user=user)
	if station_obj.exists():
		station_list = json.loads(station_obj[0].station_list)

	sensor_dict = {}
	vwc_dict = {}
	for k, v in station_list.iteritems():
		if SensorList.objects.filter(station=k).exists():
			sensor_dict.update({k:SensorList.objects.filter(station=k)[0].sensor_list})

	for k, v in sensor_dict.iteritems():
		for key, val in v.iteritems():
			if key in soil_moist_codes:
				vwc_dict.update({station_list[k]:{k:{key:val}}})

	for obj in DSensorList.objects.filter(user=user):
		if obj.sensor_list['sensor_id'] in soil_moist_codes_dg: 
			vwc_dict_dg.update({obj.sensor_id:obj.sensor_list}) 

	vwc['fc'] = vwc_dict
	vwc['dg'] = vwc_dict_dg
	return vwc


def get_all_sensors(user):
	
	vwc = {'fc':'', 'dg':''}
	vwc_dict_dg = {}

	soil_moist_codes = ['24321', '19201', '19969', '19953', '25857', '26881', '36097', '20227', '34689', '36100']
	soil_moist_codes_dg = ['253', '254', '252','249', '125', '127', '122', '120', '119']
	station_obj = StationList.objects.filter(user=user)
	if station_obj.exists():
		station_list = json.loads(station_obj[0].station_list)

	sensor_dict = {}
	vwc_dict = {}
	for k, v in station_list.iteritems():
		if SensorList.objects.filter(station=k).exists():
			sensor_dict.update({k:SensorList.objects.filter(station=k)[0].sensor_list})

	for k, v in sensor_dict.iteritems():
		int_dict = {}
		for key, val in v.iteritems():
			int_dict.update({key:val})
		vwc_dict.update({station_list[k]:{k:int_dict}})

	for obj in DSensorList.objects.filter(user=user):
		if obj.sensor_list['sensor_id'] in soil_moist_codes_dg:
			vwc_dict_dg.update({obj.sensor_id:obj.sensor_list})

	vwc['fc'] = vwc_dict
	vwc['dg'] = vwc_dict_dg
	print vwc
	return vwc



def get_dg_sensors(user):

	sensors = {}
	if DSensorList.objects.filter(user=user).exists():
		for obj in DSensorList.objects.filter(user=user):
			sensors.update({obj.sensor_id:obj.sensor_list})
	return sensors



def get_temp_sensors(user):
	
	temp = {'fc':'', 'dg':''}
	temp_dict_dg = {}
	sensor_dict = {}
	temp_dict_fc = {}
	temp_codes_fc = ['0', '16385', '506', '506', '20484', '20486', '20483', '21777']
	temp_codes_dg = ['119', '251', '159', '117', '116', '122', '120', '121']

	station_obj = StationList.objects.filter(user=user)
	if station_obj.exists():
		station_list = json.loads(station_obj[0].station_list)

	
	for k, v in station_list.iteritems():
		if SensorList.objects.filter(station=k).exists():
			sensor_dict.update({k:SensorList.objects.filter(station=k)[0].sensor_list})

	for k, v in sensor_dict.iteritems():
		for key, val in v.iteritems():
			if key in temp_codes_fc:
				temp_dict_fc.update({station_list[k]:{k:{key:val}}})

	for obj in DSensorList.objects.filter(user=user):
		if obj.sensor_list['sensor_id'] in temp_codes_dg:
			temp_dict_dg.update({obj.sensor_id:obj.sensor_list}) 

	temp['fc'] = temp_dict_fc
	temp['dg'] = temp_dict_dg
	return temp


def get_rh_sensors(user):
	
	temp = {'fc':'', 'dg':''}
	temp_dict_dg = {}
	sensor_dict = {}
	temp_dict_fc = {}
	temp_codes_fc = ['1', '507', '21778', '20226', '']
	temp_codes_dg = ['159']

	station_obj = StationList.objects.filter(user=user)
	if station_obj.exists():
		station_list = json.loads(station_obj[0].station_list)

	
	for k, v in station_list.iteritems():
		if SensorList.objects.filter(station=k).exists():
			sensor_dict.update({k:SensorList.objects.filter(station=k)[0].sensor_list})

	for k, v in sensor_dict.iteritems():
		for key, val in v.iteritems():
			if key in temp_codes_fc:
				temp_dict_fc.update({station_list[k]:{k:{key:val}}})

	for obj in DSensorList.objects.filter(user=user):
		if obj.sensor_list['sensor_id'] in temp_codes_dg:
			temp_dict_dg.update({obj.sensor_id:obj.sensor_list}) 

	temp['fc'] = temp_dict_fc
	temp['dg'] = temp_dict_dg
	return temp


def get_solar_sensors(user):
	
	temp = {'fc':'', 'dg':''}
	temp_dict_dg = {}
	sensor_dict = {}
	temp_dict_fc = {}
	temp_codes_fc = ['2', '600', '21249', '30']
	temp_codes_dg = ['250']

	station_obj = StationList.objects.filter(user=user)
	if station_obj.exists():
		station_list = json.loads(station_obj[0].station_list)

	
	for k, v in station_list.iteritems():
		if SensorList.objects.filter(station=k).exists():
			sensor_dict.update({k:SensorList.objects.filter(station=k)[0].sensor_list})

	for k, v in sensor_dict.iteritems():
		for key, val in v.iteritems():
			if key in temp_codes_fc:
				temp_dict_fc.update({station_list[k]:{k:{key:val}}})

	for obj in DSensorList.objects.filter(user=user):
		if obj.sensor_list['sensor_id'] in temp_codes_dg:
			temp_dict_dg.update({obj.sensor_id:obj.sensor_list}) 

	temp['fc'] = temp_dict_fc
	temp['dg'] = temp_dict_dg
	return temp
			

def get_wind_sensors(user):
	
	temp = {'fc':'', 'dg':''}
	temp_dict_dg = {}
	sensor_dict = {}
	temp_dict_fc = {}
	temp_codes_fc = ['16391', '5', '21009', '21010', '21012', '21011']
	temp_codes_dg = ['186']

	station_obj = StationList.objects.filter(user=user)
	if station_obj.exists():
		station_list = json.loads(station_obj[0].station_list)

	
	for k, v in station_list.iteritems():
		if SensorList.objects.filter(station=k).exists():
			sensor_dict.update({k:SensorList.objects.filter(station=k)[0].sensor_list})

	for k, v in sensor_dict.iteritems():
		for key, val in v.iteritems():
			if key in temp_codes_fc:
				temp_dict_fc.update({station_list[k]:{k:{key:val}}})

	for obj in DSensorList.objects.filter(user=user):
		if obj.sensor_list['sensor_id'] in temp_codes_dg:
			temp_dict_dg.update({obj.sensor_id:obj.sensor_list}) 

	temp['fc'] = temp_dict_fc
	temp['dg'] = temp_dict_dg
	return temp



@login_required
def get_widget(request):
	print 'in get_widget'
	if request.is_ajax():
		if request.method == 'POST':
			post_data = json.loads(request.body)
			if Widgets.objects.filter(user=request.user, widget_id=post_data['id']).exists():
				new_widget = set_widget(post_data, request.user)
				Widgets.objects.filter(user=request.user, widget_id=post_data['id']).update(widget=new_widget)
				return HttpResponse(json.dumps(new_widget))
			else:
				new_widget = set_widget(post_data, request.user)
				widget = Widgets(user=request.user, widget_id=new_widget['id'], widget_type=new_widget['type'], widget=new_widget)
				widget.save()
				return HttpResponse(json.dumps(new_widget))

	return HttpResponse(json.dumps(post_data)) # return http bad request

	# widget_objs = Widgets.objects.filter(user=user.user)

	# for widget in widget_objs:
	# 	if widget.widget_id == widget_id:
	# 		return widget
	# return None 

# // description of widget dictionary (object) :
# // options: name(string), chart-type(string), colors(array/list),
#  //data: {'sensor': {'db':'dg[,fc]', 'sensors': {'temp':10, 'moist': 15}}, 'calc':{'paw':{'db':{'station':station, 'sensor':[], 'value':value},
#   //'fc':[temp, moist], 'value':null},'degree_days': {'dg':[temp, moist], 'fc':[temp, moist], 'value':null}, 'chilling_hours': {'dg':[temp, moist], 'fc':[temp, moist], 'value':null}}}

# 	data = {'calc':{'params':{'db':$db, 'station':$station, 'sensor':$stat_data}, 'value':null}}

def set_widget(widget_dict, user):
	print 'in set_widget: ', widget_dict
	if widget_dict['type'] == 'stat':
		if widget_dict['data'].has_key('calc'):
			for k, v in widget_dict['data'].iteritems():
				if v['params']['sensor'] == 'degree_days_acc':
					widget_dict['data']['calc']['value'] = degree_days_acc(user, v['params']['db'], v['params']['station_id'])
				elif v['params']['sensor'] == 'temp_min':
					widget_dict['data']['calc']['value'] = temp_min(user, v['params']['db'], v['params']['station_id'], 24)
				elif v['params']['sensor'] == 'temp_max':
					widget_dict['data']['calc']['value'] = temp_max(user, v['params']['db'], v['params']['station_id'], 24)
				elif v['params']['sensor'] == 'temp_avg':
					widget_dict['data']['calc']['value'] = temp_avg(user, v['params']['db'], v['params']['station_id'], 24)
				elif v['params']['sensor'] == 'chilling_hours_acc':
					print 'is chilling_hours_acc'
					widget_dict['data']['calc']['value'] = chilling_hours_acc(user, v['params']['db'], v['params']['station_id'])
	elif widget_dict['type'] == 'main-chart':
		print 'widget type main-chart'
		for key, val in widget_dict['data'].iteritems():
			print 'no prob. here'
			if key == 'evapo':
				if val is not None:
					print 'evapo request'
					widget_dict['data']['evapo']['value'] = get_eto_data(widget_dict, user)
			elif key == 'paw':
				if val is not None:
					paw_data = get_paw_data(widget_dict, user)
					widget_dict['data']['paw']['value'] = paw_data
					widget_dict['data']['paw']['lineColor'] = paw_data[0]['lineColor']
			elif key == 'raw_sensors':
				if val is not None:
					print 'raw sensor request'
					widget_dict['data']['raw_sensors']['value'] = get_raw_data(widget_dict, user)
			elif key == "dew_point":
				if val is not None:
					widget_dict['data']['dew_point']['value'] = get_dew_point_data(widget_dict, user)
			elif key == 'chilling_portions':
				print 'chilling_portions request'
				if val is not None:
					widget_dict['data']['chilling_portions']['value'] = get_chip_data(widget_dict, user)
					print widget_dict['data']['chilling_portions']['value']



	return widget_dict

	# raw_sensors = {'params':{'sensors':main_sensors}, 'value':''};
	# 		paw = {'params':{'fc':main_paw_fc, 'wp':main_paw_wp, 'sensors':main_paw_sensors}, 'value':''};
	# 		chilling_portions = {'params':{'sensors':main_cp}, 'value':''};
	# 		degree_days = {'params': {'sensors':main_dd, 'th':main_dd_th}, 'value':''};
	# 		chilling_hours = {'params': {'sensors':main_ch, 'th':main_ch_th}, 'value':''}
	# 		dew_point = {'params':{'sensors':'', 'rh':main_dp_rh, 'remp': main_dp_t}, 'value':''}
	# 		evapo = {'params': {
	# 			'sensors':'', 'temp':main_eto_t,
	# 			'rh':main_eto_rh,
	# 			'sr':main_eto_sr,
	# 			'ws':main_eto_ws,
	# 			'lat':main_eto_lat, 
	# 			'alt':main_eto_alt},
	# 		'value':''
	# 	}
	# def get_record(user, station_name, date_from, date_to, sensor='0'):
	# $data = {
	# 		'raw_sensors':raw_sensors,
	# 		'paw':paw,
	# 		'chilling_portions':chilling_portions,
	# 		'degree_days':degree_days,
	# 		'chilling_hours':chilling_hours,
	# 		'evapo':evapo,
	# 		'dew_point':dew_point,
	# 		'calc': {'params':{'sensor':'temp_min'}},
	# 		'range': {'from':$date_from, 'to':$date_to}
	# 	}

def has_data(data_lst):
	i = 0
	if data_lst != []:
		while i < 10 and i < len(data_lst):
			print 'good in has data'
			if data_lst[i]['value'] == 0.0:
				i +=1
			elif data_lst[i]['value'] != 0.0:
				return True
		if i > 8:
			return False
	else:
		return False


def get_temp_data(user, db, station, dt_from, dt_to):
	print 'getting Temperature data'
	fc_sensors = ['0', '16385', '506', '20484', '20486', '20483', '21777']
	dg_sensors = [] # update this!
	appuser = AppUser.objects.get(user=user)
	if db == 'fc':
		print 'fc True'
		sensors = get_sensor_list(appuser, station)
		print sensors
		for k, v in sensors.iteritems():
			if k in fc_sensors:
				print 'k in sensors'
				data_list = get_sensor_data(k, load_station_data, user, db, station, dt_from, dt_to)
				print data_list
				if has_data(data_list):
					return data_list
	elif db == 'dg':
		pass

	return False


def temp_min(user, db, station, period):
	global HOUR
	minmax = get_minmax(user, db, station)
	max_entry = parse_date_s(minmax['f_date_max'])
	dt_from = max_entry - timedelta(hours=period)
	print ' good upto here'
	print max_entry
	print dt_from
	temp_data = get_temp_data(user, db, station, dt_from, max_entry - HOUR)
	print temp_data
	if not temp_data:
		return 0

	value_lst = [rec['value'] for rec in temp_data]
	return min(value_lst)


def temp_max(user, db, station, period):
	global HOUR
	minmax = get_minmax(user, db, station)
	max_entry = parse_date_s(minmax['f_date_max'])
	dt_from = max_entry - timedelta(hours=period)
	print ' good upto here'
	print max_entry
	print dt_from
	temp_data = get_temp_data(user, db, station, dt_from, max_entry - HOUR)
	print temp_data
	if not temp_data:
		return 0

	value_lst = [rec['value'] for rec in temp_data]
	return max(value_lst)

def temp_avg(user, db, station, period):
	global HOUR
	minmax = get_minmax(user, db, station)
	max_entry = parse_date_s(minmax['f_date_max'])
	dt_from = max_entry - timedelta(hours=period)
	print ' good upto here'
	print max_entry
	print dt_from
	temp_data = get_temp_data(user, db, station, dt_from, max_entry - HOUR)
	print temp_data
	if not temp_data:
		return 0

	value_lst = [rec['value'] for rec in temp_data]
	return round(sum(value_lst)/len(value_lst),2)

def degree_days_acc(user, db, station):
	return 350

def chilling_hours_acc(user, db, station):
	return 260


def get_raw_data(widget_data, user):
	print 'getting raw sensor data'
	global DAY
	daily_avg = []
	params = widget_data['data']['raw_sensors']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	eto_sensors = ['1201', '720']
	chart_type = "line"
	sensor_name = ""
	station_name = ""
	if params.has_key('sensors'):
		sensors = params['sensors']
		if len(sensors) == 1:
			sens = sensors[0].split('-')
			if sens[2] in eto_sensors:
					chart_type = 'column'
			if SensorCodes.objects.filter(user=user, sensor_id=sens[2]).exists():
				sensor_name = SensorCodes.objects.get(user=user, sensor_id=sens[2]).sensor_name #get sensor name to inject
			if sens[0] == 'fc':
				sensor_data = get_sensor_data(sens[2], load_station_data, user, sens[0], sens[1], dt_from, dt_to)
				sensor_data[0].update({'name':sensor_name, 'station':sens[1], 'type':chart_type}) # insert sensor code into the first entry
				print sensor_data
				daily_avg.extend([sensor_data])
			else:
				#dg code
				pass
		elif len(sensors) > 1:
			for i, v in enumerate(sensors):
				sens = v.split('-')
				if sens[2] in eto_sensors:
					chart_type = 'column'
				if SensorCodes.objects.filter(user=user, sensor_id=sens[2]).exists():
					sensor_name = SensorCodes.objects.get(user=user, sensor_id=sens[2]).sensor_name
				if sens[0] == 'fc':
					sensor_data = get_sensor_data(sens[2], load_station_data, user, sens[0], sens[1], dt_from, dt_to)
					sensor_data[0].update({'name':sensor_name, 'station':sens[1], 'type':chart_type}) # insert sensor code into the first entry
					print sensor_data
					daily_avg.extend([sensor_data])
				else:
					pass
	else:
		pass

	return daily_avg



def  get_paw_data(widget_data, user):
	print 'getting paw data'
	raw_values = {}
	params = widget_data['data']['paw']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	fc = params['fc']
	wp = params['wp']
	line_color = '#00fff7'
	if params.has_key('sensors'):
		sensors = params['sensors']
		if len(sensors) > 1:
			line_color = '#000000'
			for i, sensor in enumerate(sensors):
				sens = sensor.split('-')
				if sens[0] == 'fc':
					data_list = get_sensor_data(sens[2], load_station_data, user, sens[0], sens[1], dt_from, dt_to)
					raw_values.update({sens[0]:{v['date']:v['value'] for i, v in enumerate(data_list)}})
				else:
					pass
		elif len(sensors) == 1:
			sens = sensors[0].split('-')
			if sens[0] == 'fc':
				data_list = get_sensor_data(sens[2], load_station_data, user, sens[0], sens[1], dt_from, dt_to)
				raw_values.update({sens[2]:{v['date']:v['value'] for i, v in enumerate(data_list)}})
			else:
				pass
	else:
		pass
	paw_values = paw(int(fc), int(wp), raw_values)
	ret_values = [{'date':v['date'], 'value':v['value']} for i, v in enumerate(paw_values)]
	srtd_values = sorted(ret_values, key=lambda k: k['date'])
	srtd_values[0].update({'lineColor':line_color})
	return srtd_values




def get_eto_data(widget_data, user):
	print 'calculating eto'
	global DAY
	daily_eto = []
	params = widget_data['data']['evapo']['params'] #(user, db, station, dt_from, dt_to)
	dt_from = parse_date(widget_data['data']['range']['from'])
	print dt_from
	dt_to = parse_date(widget_data['data']['range']['to'])
	print dt_to
	if params.has_key('temp'):
		s_temp = params['temp'].split('-')
		if s_temp[0] == 'fc':
			temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], dt_from, dt_to)
			t_min = {v['date']:v['value'] for i, v in enumerate(get_daily_min(temp_data))}
			t_max = {v['date']:v['value'] for i, v in enumerate(get_daily_max(temp_data))}
			t_avg = {v['date']:v['value'] for i, v in enumerate(get_daily_avg(temp_data))}
			s_rh = params['rh'].split('-')
			rh = get_sensor_data(s_rh[2], load_station_data, user, s_rh[0], s_rh[1], dt_from, dt_to)
			rh_min = {v['date']:v['value'] for i, v in enumerate(get_daily_min(rh))}
			rh_max = {v['date']:v['value'] for i, v in enumerate(get_daily_max(rh))}
			s_sr = params['sr'].split('-')
			sr = get_sensor_data(s_sr[2], load_station_data, user, s_sr[0], s_sr[1], dt_from, dt_to)
			print sr
			sr_avg = {v['date']:v['value'] for i, v in enumerate(get_daily_avg(sr))}
			s_ws = params['ws'].split('-')
			ws = get_sensor_data(s_ws[2], load_station_data, user, s_ws[0], s_ws[1], dt_from, dt_to)
			print ws
			ws_avg = {v['date']:v['value'] for i, v in enumerate(get_daily_avg(ws))}
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
					daily_eto.extend([{'date':start_day, 'value':evapotranspiration(sr_avg[start_day], float(alt), t_max[start_day], t_min[start_day], rh_min[start_day], rh_max[start_day], day, float(lat), t_avg[start_day], ws_avg[start_day])}])
				start +=DAY
	print 'daily_eto returning'
	print daily_eto
	return daily_eto


def get_dew_point_data(widget_data, user):
	print 'Calculating dew point ...'
	global DAY
	daily_dp = []
	params = widget_data['data']['dew_point']['params'] #(user, db, station, dt_from, dt_to)
	dt_from = parse_date(widget_data['data']['range']['from'])
	print dt_from
	dt_to = parse_date(widget_data['data']['range']['to'])
	print dt_to
	if params.has_key('temp'):
		s_temp = params['temp'].split('-')
		if s_temp[0] == 'fc':
			temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], dt_from, dt_to)
			t_avg = {v['date']:v['value'] for i, v in enumerate(get_daily_avg(temp_data))}
			s_rh = params['rh'].split('-')
			rh = get_sensor_data(s_rh[2], load_station_data, user, s_rh[0], s_rh[1], dt_from, dt_to)
			rh_avg = {v['date']:v['value'] for i, v in enumerate(get_daily_avg(rh))}
			start = dt_from
			end = dt_to
			while start <= end:
				start_day = start.strftime('%Y-%m-%d')
				if t_avg.has_key(start_day) and rh_avg.has_key(start_day):
					daily_dp.extend([{'date':start_day, 'value':dew_point(t_avg[start_day], rh_avg[start_day])}])
				start +=DAY
	print 'daily_dp returning'
	print daily_dp
	return daily_dp

def calculate_chip(temp_data, sensor_id, dt_from, dt_to, prev_portions):
	print 'Processing chilling_portions data ...'
	print 'from: ', dt_from
	print 'to: ', dt_to
	RESET_DATE = '' # user settings

	for i, v in enumerate(temp_data):
		print 'enumerating ...'
		if dt_from <= parse_date(v['date']) <= dt_to:
			if v['date'] == RESET_DATE: # feb at 12:00 ??
				prev_portions = {'xi':0.0, 'inter_e':0.0, 'delt':0.0, 'portions':0.0}
			print 'one record down ...'
			portions = chill_portions(v['value'], prev_portions)
			print v['date'], portions
			prev_portions = portions
			obj = Chip(date=v['date'], sensor_id=sensor_id, value=portions)
			obj.save()



def get_chip_data(widget_data, user):
	print 'Calculating chilling portions ... '
	daily_chip = []
	params = widget_data['data']['chilling_portions']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])
	first_record = ''
	last_record = ''
	prev_zero = {'xi':0.0, 'inter_e':0.0, 'delt':0.0, 'portions':0.0}
	if params.has_key('sensors'):
		print 'has_key sensors'
		s_temp = params['sensors'].split('-')
		if s_temp[0] == 'fc':
			print 'is fc indeed'
			chip_record = Chip.objects.filter(sensor_id=s_temp[1]+s_temp[2])
			if chip_record.exists():
				print 'record exists'
				first_record = chip_record.first()
				last_record = chip_record.last()
				print '--------------get chip data -----------------'
				print first_record.date
				print last_record.date
				print '------------from and to -----------'
				print dt_from
				print dt_to
				if first_record.date <= dt_from <= last_record.date and first_record.date <= dt_to <= last_record.date:
					return [{'date':record.date.strftime('%Y-%m-%d %H:%M'), 'value': record.value['portions']} for record in chip_record if record.date >= dt_from and record.date <= dt_to]
				elif dt_to < first_record.date:
					print 'dt_to < first_record.date'
					temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], dt_from, dt_to)
					calculate_chip(temp_data, s_temp[1]+s_temp[2], dt_from, first_record.date, prev_zero)
					return get_chip_data(widget_data, user)
				elif dt_from > last_record.date:
					print 'dt_from > last_record.date'
					temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], last_record.date, dt_to)
					calculate_chip(temp_data, s_temp[1]+s_temp[2], last_record.date, dt_to, last_record.value) # previous portions must not be written over in case duplicate record
					return get_chip_data(widget_data, user)
				elif dt_from < first_record.date and first_record.date <= dt_to <= last_record.date:
					print 'dt_from < first_record.date and first_record.date <= dt_to <= last_record.date'
					temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], dt_from - (2*HOUR), dt_to + HOUR)
					calculate_chip(temp_data, s_temp[1]+s_temp[2], dt_from - (2*HOUR), first_record.date + HOUR, prev_zero)
					return get_chip_data(widget_data, user)
				elif first_record.date <= dt_from <= last_record.date and last_record.date < dt_to:
					print 'first_record.date <= dt_from <= last_record.date and last_record.date < dt_to'
					temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], dt_from, dt_to)
					calculate_chip(temp_data, s_temp[1]+s_temp[2], dt_from - (2*HOUR), dt_to + HOUR, last_record.value)
					return get_chip_data(widget_data, user)
				elif dt_from < first_record.date and last_record.date < dt_to:
					print 'dt_from < first_record.date and last_record.date < dt_to'
					temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], dt_from, dt_to)
					calculate_chip(temp_data, s_temp[1]+s_temp[2], dt_from, first_record.date, prev_zero)
					calculate_chip(temp_data, s_temp[1]+s_temp[2], last_record.date, dt_to, last_record.value)
					return get_chip_data(widget_data, user)
			else:
				print 'no previous calculations exist'
				temp_data = get_sensor_data(s_temp[2], load_station_data, user, s_temp[0], s_temp[1], dt_from, dt_to)
				print 'got temp_data .......'
				calculate_chip(temp_data, s_temp[1]+s_temp[2], dt_from, dt_to, prev_zero)
				return get_chip_data(widget_data, user)
		elif s_temp[0] == 'dg':
			pass
			# dg code here

def get_cportions_data(widget_data, user):
	print 'Calculating chilling portions '
	daily_chip = []
	params = widget_data['data']['chilling_portions']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])

	if not params.has_key('sensors'):
		return False

	print 'has key sensors: True'
	s_temp = params['sensors'].split('-')

	if s_temp[0] == 'fc':
		print 'Retrieving fieldclimate data from local database...'
		RESET_DATE = '02-01' + '00:00'
		YEAR = dt_from.YEAR
		max_entry = StationData.objects.filter(station_id=s_temp[1]+'-'+s_temp[2], database=s_temp[0]).last().date
		raw_data = load_data(s_temp[2], s_temp[1], parse_date(YEAR+RESET_DATE), max_entry)
		cportions = calculate_cportions(raw_data)
		return [{'date':portions.date, 'value':portions.value} for portions in cportions if dt_from <= portions.date <= dt_to]

	elif s_temp[0] == 'dg':
		print 'Retrieving decagon data from local database...'
		RESET_DATE = '02-01' + '00:00'
		YEAR = dt_from.YEAR
		max_entry = StationData.objects.filter(station_id=s_temp[1]+'-'+s_temp[2]+'-'+s_temp[3], database=s_temp[0]).last().date
		raw_data = load_data(s_temp[2]+'-'+s_temp[3],s_temp[1], parse_date(YEAR+RESET_DATE), max_entry)
		cportions = calculate_cportions(raw_data)
		return [{'date':portions.date, 'value':portions.value} for portions in cportions if dt_from <= portions.date <= dt_to]
	return False

def calculate_cportions(raw_data, sensor_id):
	cportions = []
	prev_portions = {'xi':0.0, 'inter_e':0.0, 'delt':0.0, 'portions':0.0, 'accumulation':0.0}	
	for data in raw_data:
		portions = chill_portions(data, prev_portions)
		cportions.extend(portions)
		prev_portions = portions
	return cportions

def get_chill_hours_data(widget_data, user):
	print 'Retrieving tempreture data for chill hours calculation...'
	params = widget_data['data']['chilling_portions']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])

	if not params.has_key('sensors'):
		return False
	print 'has key sensors: True'
	s_temp = params['sensors'].split('-')
	if s_temp[0] == 'fc':
		print 'Retrieving fieldclimate data from local database...'
		RESET_DATE = '02-01' + '00:00'
		YEAR = dt_from.YEAR
		max_entry = StationData.objects.filter(station_id=s_temp[1]+'-'+s_temp[2], database=s_temp[0]).last().date
		raw_data = load_data(s_temp[2], s_temp[1], parse_date(YEAR+RESET_DATE), max_entry)
		chill_hours_acc = calculate_chill_hours(raw_data)
		return [{'date': hours.date, 'value':hours.value} for hours in chill_hours if dt_from <= hours.date <= dt_to]
	elif s_temp[0] == 'dg':
		print 'Retrieving decagon data for chiling hours calculation from local database...'
		RESET_DATE = '02-01' + '00:00'
		YEAR = dt_from.YEAR
		max_entry = StationData.objects.filter(station_id=s_temp[1]+'-'+s_temp[2]+'-'+s_temp[3], database=s_temp[0]).last().date
		raw_data = load_data(s_temp[2]+'-'+s_temp[3], s_temp[1], parse_date(YEAR+RESET_DATE), max_entry)
		chill_hours_acc = calculate_chill_hours(raw_data)
		return [{'date': hours.date, 'value':hours.value} for hours in chill_hours if dt_from <= hours.date <= dt_to]
	return False


def calculate_chill_hours(raw_data, threshold):
	chill_hours_acc = []
	date1 = raw_data[0]['date']
	accumulation = 0
	for data in raw_data:
		if chill_hours(data['value'], threshold):
			if (data.date - date1) >= HOUR:
				accumulation += 1
				date1 = data.date
				chill_hours_acc.extend({'date': data.date, 'value':accumulation})
			else:
				chill_hours_acc.extend({'date': data.date, 'value':accumulation})
		else:
			date1 = data.date
			chill_hours_acc.extend({'date': data.date, 'value': accumulation})

	return chill_hours_acc


def get_degree_days_data(widget_data, user):
	print 'Retrieving tempreture data for degree days calculation...'
	params = widget_data['data']['degree_days']['params']
	dt_from = parse_date(widget_data['data']['range']['from'])
	dt_to = parse_date(widget_data['data']['range']['to'])

	if not params.has_key('sensors'):
		return False
	print 'has key sensors: True'
	s_temp = params['sensors'].split('-')
	if s_temp[0] == 'fc':
		print 'Retrieving fieldclimate data for degree days calculation from local database...'
		RESET_DATE = '02-01' + '00:00'
		YEAR = dt_from.YEAR
		max_entry = StationData.objects.filter(station_id=s_temp[1]+'-'+s_temp[2], database=s_temp[0]).last().date
		raw_data = load_data(s_temp[2], s_temp[1], parse_date(YEAR+RESET_DATE), max_entry)
		degree_days_acc = calculate_degree_days(raw_data)
		return [{'date': degrees.date, 'value':degrees.value} for degrees in degree_days_acc if dt_from <= degrees.date <= dt_to]
	elif s_temp[0] == 'dg':
		print 'Retrieving decagon data for degree days calculation from local database...'
		RESET_DATE = '02-01' + '00:00'
		YEAR = dt_from.YEAR
		max_entry = StationData.objects.filter(station_id=s_temp[1]+'-'+s_temp[2]+'-'+s_temp[3], database=s_temp[0]).last().date
		raw_data = load_data(s_temp[2]+'-'+s_temp[3], s_temp[1], parse_date(YEAR+RESET_DATE), max_entry)
		degree_days_acc = calculate_degree_days(raw_data)
		return [{'date': degrees.date, 'value':degrees.value} for degrees in degree_days_acc if dt_from <= degrees.date <= dt_to]
	return False


def calculate_degree_days(raw_data, threshold):
	degree_days_acc = []
	date1 = raw_data[0]['date']
	accumulation = 0
	for data in raw_data:
		if degree_days(data['value'], threshold):
			if (data.date - date1) >= HOUR:
				accumulation += 1
				date1 = data.date
				degree_days_acc.extend({'date': data.date, 'value':accumulation})
			else:
				degree_days_acc.extend({'date': data.date, 'value':accumulation})
		else:
			date1 = data.date
			degree_days_acc.extend({'date': data.date, 'value': accumulation})

	return degree_days_acc




def load_data(station_id, sensor, database, dt_from, dt_to):
	records = StationData.objects.filter(station_id=station_id, database=database)
	if not records.exists():
		return []
	if database == 'dg': #decagon
		return [{'date': record.data['date'], 'value': record.data['sensor']} for record in reocrds if dt_from >= record.date <= dt_to]
	elif database == 'fc': #fieldcliamte
		json_res = []
		for i, v in enumerate(records):
			temp_dict = {}
			for key, val in v.iteritems():
				temp_dict.update({key.split('_')[len(key.split('_'))-1]:val})
			json_res.extend([temp_dict])

		return_set = []
		for k, v in enumerate(json_res):
			if v.has_key(sensor):
				value = v[sensor]
				if value is None:
					value = 0
				return_set.extend([{"date":parse_date_s(v['date']).strftime('%Y-%m-%d %H:%M'), "value": float(value)}])
		return return_set	


def load_widgets(user):

	data_dict = {'degree_days_acc': 'Degree Days Accu.', 'temp_min':'Min Temperature', 'temp_avg':'Avg. Temperature',
	 'temp_max': 'Max Temperature', 'chilling_hours_acc':'Chilling Hours Accu.'}
	widget_dict = {}
	widgets = Widgets.objects.filter(user=user)
	if widgets.exists():
		for widget in widgets:
			widget_dict.update({widget.widget_id:{'widget':widget.widget, 'w_json':json.dumps(widget.widget), 'sensor':data_dict[widget.widget['data']['calc']['params']['sensor']]}})
		print json.dumps(widget.widget)	
	return widget_dict





def save(user, db, station_name, f_date, data):
	date = parse_date(parse_date_s(f_date).strftime('%Y-%m-%d %H:%M'))
	dupl_record = Station_Data.objects.filter(user=user, database=db, station_name=station_name, f_date=date)
	if dupl_record.exists():
		return
	record = Station_Data(user=user, database=db, station_name=station_name, f_date=date, data=data)
	record.save()


def get_station_data(user, db, station_name, date_from, date_to):
	minmax = get_minmax(user, db, station_name)
	max_entry = parse_date_s(minmax['f_date_max'])
	min_entry = parse_date_s(minmax['f_date_min'])

	print 'date_from in get stat: ', date_from
	print 'date_to in get stat: ', date_to
	if date_to > max_entry:
		date_to = max_entry
		if not date_from < date_to:
			date_from = date_to - DAY

	if date_from < min_entry:
		date_from = min_entry
		if not date_to > date_from:
			date_to = max_entry #date_from + DAY
	row_count = get_row_count(user, db, station_name, date_from, max_entry) # changed from date_to to max_entry
	print '----------------', row_count
	print '----------------max_entry', max_entry
	print '----------------from', date_from

	# if row_count < 48:
	# 	diff = 96 - row_count
	# 	row_count += diff
	# 	date_from -= DAY
	
	fc_acc = AppUser.objects.get(user=user)
	if db == 'fc':
		print 'Accessing remote DB ...'
		response = requests.post("http://fieldclimate.com/api/index.php?action=CIDIStationData_GetFromDate",
		 data={"user_name": fc_acc.fc_username, "user_passw" : fc_acc.fc_password, "station_name": station_name,\
		  'dt_from':date_from.strftime('%Y-%m-%d %H:%M'), 'row_count':row_count})
		if is_json(response.text):
			if json.loads(response.text).has_key('ReturnDataSet'):
				print 'Saving new data to database ...'
				for i, v in enumerate(json.loads(response.text)['ReturnDataSet']):
					save(user, db, station_name, v['f_date'], v)
			else:
				print 'Problem accessing remote DB. Retrying ...'
				get_station_data(user, db, station_name, date_from, date_to)
		else:
			print 'Problem accessing remote DB. Retrying ...'
			get_station_data(user, db, station_name, date_from, date_to)


	elif db == 'dg':
		pass


def get_sensor_data(sensor, get_data, *args):
	print 'Processing new data ...'
	data = get_data(*args)
	json_res = []
	for i, v in enumerate(data):
		temp_dict = {}
		for key, val in v.iteritems():
			temp_dict.update({key.split('_')[len(key.split('_'))-1]:val})
		json_res.extend([temp_dict])

	return_set = []
	for k, v in enumerate(json_res):
		if v.has_key(sensor):
			value = v[sensor]
			if value is None:
				value = 0
			return_set.extend([{"date":parse_date_s(v['date']).strftime('%Y-%m-%d %H:%M'), "value": float(value)}])
	return return_set


def load_station_data(user, db, station, dt_from, dt_to):
	print 'Loading requested station data ...'

	minmax = get_minmax(user, db, station)
	max_entry = parse_date_s(minmax['f_date_max'])
	min_entry = parse_date_s(minmax['f_date_min'])
	if dt_to > max_entry:
		dt_to = max_entry
	if dt_from < min_entry:
		dt_from = min_entry
	print '-----------------minmax --------------'
	print min_entry
	print max_entry

	if db == 'fc':
		records = Station_Data.objects.filter(user=user, database=db, station_name=station)
		if not records.exists():
			if not dt_from < dt_to:
				return False
			get_station_data(user, db, station, dt_from, dt_to)
			return load_station_data(user, db, station, dt_from, dt_to)
		if not dt_from < dt_to:
			return False
		print 'Requested data range: ', dt_from, dt_to
		if records.first().f_date <= dt_from <= records.last().f_date:
			if records.first().f_date <= dt_to - HOUR <= records.last().f_date:
				return_set = [rec.data for rec in records if rec.f_date > dt_from and rec.f_date < dt_to]
				print 'Returning new data from DB ...'
				return return_set
			print 'Data partly present in local DB. Getting remaining from remote DB ...'
			print '----------------------last', records.last().f_date
			print '----------------------to', dt_to
			print '----------------------from', dt_from

			get_station_data(user, db, station, records.last().f_date, dt_to)	
			return load_station_data(user, db, station, dt_from, dt_to)
		elif records.first().f_date <= dt_to <= records.last().f_date:
			print 'Data partly present in local DB. Getting older records from remote DB ...'
			get_station_data(user, db, station, dt_from - HOUR, records.first().f_date)
			return load_station_data(user, db,station, dt_from, dt_to)
		elif dt_to < records.first().f_date:
			print 'Data not presen in local DB. Getting old data from remote DB ...'
			get_station_data(user, db, station, dt_from, records.first().f_date)
			return load_station_data(user, db, station, dt_from, dt_to)
		elif dt_from > records.last().f_date:
			print 'Data not present in local DB. Getting new data from remote DB ...'
			get_station_data(user, db, station, records.last().f_date, dt_from)
			get_station_data(user, db, station, records.last().f_date, dt_to)
			return load_station_data(user, db, station, dt_from, dt_to)
		else:
			print 'Data not present in local DB. Getting data from remote DB ...'
			get_station_data(user, db, station,  dt_from, records.first().f_date)
			get_station_data(user, db, station, records.last().f_date, dt_to)
			return load_station_data(user, db, station, dt_from, dt_to)
	elif db == 'dg':
		pass

	return False



@login_required()
def get_data(request):


	if request.GET.get('station_name','') == '' or request.GET.get('sensor','') == '':
		return HttpResponse('parameter missing, bad request') # should return http bad requests code

	if request.GET.get('row_count', '') == '':
		row_count = 200
	else:
		row_count = int(request.GET['row_count'])

	response = get_record(station_name=request.GET['station_name'], sensor=request.GET['sensor'], value=1, row_count=row_count, user=request.user)
	
	return HttpResponse(response)

	#return HttpResponse('row count: ' + str(row_count) + '| station name: ' + request.GET['station_name'] + '| sensor: ' + request.GET['sensor'] + '  ' + request.user.username)


@login_required()
def get_paw(request):


	if request.GET.get('station_name','') == '' or request.GET.get('sensor','') == '':
		return HttpResponse('parameter missing, bad request') # should return http bad requests code

	if request.GET.get('row_count', '') == '':
		row_count = 200
	else:
		row_count = int(request.GET['row_count'])

	if request.GET.get('fc', '') == '':
		fc = 10
	else:
		fc = int(request.GET['fc'])

	if request.GET.get('wp', '') == '':
		wp = 10
	else:
		wp = int(request.GET['wp'])

	response = paw(user=request.user, station=request.GET['station_name'], fc=request.GET['fc'], wp=request.GET['wp'], sensors=request.GET['sensor'], row_count=row_count)
	
	return HttpResponse(json.dumps(response, sort_keys=True))


def set_password(self, raw_password):
	self.fc_salt = uuid.uuid4().hex
	self.fc_password = hashlib.sha512(fc_password + salt).hexdigest()

#@csrf_exempt
def get_test(request):


	if request.method == 'GET':
		return HttpResponse("its a GET")
	elif request.method == 'POST':
		
		res_data = json.loads(request.body)
		if res_data['size'] == '':
			return HttpResponse("post parameters missing") # return http bad request
		else:
			widget = Widgets(user=request.user, widget_id=res_data['wid'], widget=res_data)
			widget.save()
			return HttpResponse("OK!")

@login_required
@csrf_exempt
def ajax_test(request):

	station_dict = json.loads(get_station_list(AppUser.objects.get(user=request.user)))
	sensor_dict = get_sensor_list(AppUser.objects.get(user=request.user), "00001009")
	station_sensor_dict = get_station_sensor_list(AppUser.objects.get(user=request.user))

	return render(request, 'ajax_test.html', {'station_list': station_dict, 'sensor_list': sensor_dict, 'station_sensor': station_sensor_dict})


def user_settings(user):
	print 'Getting user settings ...'
	sensor_recs = SensorCodes.objects.filter(user=user)
	print 'got user list'
	info_dict = {'sensor_info':{}}
	for rec in sensor_recs:
		info = {rec.sensor_id:{'code':rec.sensor_id, 'name':rec.sensor_name, 'unit':rec.sensor_unit}}
		info_dict['sensor_info'].update(info)
	return info_dict
	

def add_fc_station(user, data):
	print 'adding station'

	try:
		fc_acc = AppUser.objects.get(user=user)
		response = requests.post("http://www.fieldclimate.com/api/CIDIUser/AddStation",
			data={"user_name": fc_acc.fc_username, "user_passw" : fc_acc.fc_password,\
			 "station_name": data['station_id'],"station_key":data['password'], "user_station_name":data['alias']})
	except requests.exceptions.RequestExcept as e:
		print e
		return add_fc_station(user, data)
	print response
	print response.text
	if response.status_code == 200:
		res = json.loads(response.text)
		if res.has_key('faultcode'):
			data['success'] = False
			data['message'] = res['faultstring']
			return data
		elif res.has_key('user_name'):
			get_station_list(fc_acc)
			data['success'] = True
			return data
	else:
		data['success'] = False
		return data

def add_dg_station(user, data):
	print 'Adding decagon station ...'

	if MyDevices.objects.filter(device=data['station_id']).exists():
		data['success'] = False
		data['message'] = 'Station already exists.'
		return data

	try:
		dg_acc = AppUser.objects.get(user=user)
		params = {'email': dg_acc.dg_username, 'userpass': dg_acc.dg_password, 'deviceid': data['station_id'], 'devicepass': data['password'], 'report': 0, 'User-Agent': 'AgViewer_1.0'}
		url = 'http://api.ech2odata.com/morph2ola/dxd.cgi'
		response = requests.post(url, data=params)
	except requests.exceptions.RequestExcept as e:
		print e

	if response.status_code == 200:
		device = MyDevices(user=user, device=data['station_id'], code=data['password'])
		device.save()
		data['success'] = True
		data['message'] = 'Station successfully added. Please refresh page.'
		return data
	else:
		data['success'] = False
		data['message'] = 'Error adding station. Please retry.'
		return data


def list_files(user):
	files = Files.objects.filter(user=user)
	if files.exists():
		file_lst = [file.file.name for file in files if file.file.name.split('.')[-2] != 'kmz'] #list only files with .kmz or .kml extension
		return file_lst
	return []