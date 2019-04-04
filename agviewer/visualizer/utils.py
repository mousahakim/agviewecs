from __future__ import division
import datetime, time, json, requests, tempfile, os, calendar
from datetime import timedelta
from django.utils import timezone
from visualizer.models import AppUser, Files
from zipfile import ZipFile
from django.conf import settings
from django.core.files import File
from django.contrib.auth.models import User
from time import strftime, gmtime
from hashlib import sha256
import hmac

MAX_RETRY = 3

def parse_date(date_string):
	frmt = '%Y-%m-%d %H:%M'
	try:
		if len(date_string.split(' ')[1]) > 5:
			frmt = '%Y-%m-%d %H:%M:%S'
	except IndexError as e:
		print e
		return parse_date_d(date_string)
	return datetime.datetime.strptime(date_string, frmt)

def parse_date_s(date_string):
	frmt = '%Y-%m-%d %H:%M:%S'
	return datetime.datetime.strptime(date_string, frmt)

def parse_date_d(date_string):
	frmt = '%Y-%m-%d'
	return datetime.datetime.strptime(date_string, frmt)

def dayofyear(date_string):
	frmt = '%Y-%m-%d %H:%M'
	return datetime.datetime.strptime(date_string, frmt).timetuple().tm_yday

def decatime(seconds):
	DIFF = 946684800
	return time.strftime('%Y-%m-%d %H:%M', time.gmtime(int(seconds)+DIFF))

def is_json(json_str):
	try:
		json_obj = json.loads(json_str)
	except ValueError, e:
		return False
	return True
	
def date_to_string(date):
	return date.strftime('%Y-%m-%d %H:%M')

# def get_minmax(user, db, station):
# 	from visualizer.models import AppUser
# 	fc_acc = AppUser.objects.get(user=user)
# 	print 'Determining min and max dates for available data ...'
# 	global MAX_RETRY
# 	print MAX_RETRY
# 	if db == 'fc':
# 		try:
# 			response = requests.post("http://fieldclimate.com/api/CIDIStationData/GetMinMaxDate",
# 		 	data={"user_name": fc_acc.fc_username, "user_passw" : fc_acc.fc_password, "station_name": station})
# 		 	print 'in minmax ', response.status_code
# 		 	print response.text
# 		except requests.exceptions.RequestException as e:
# 			print e
# 			if MAX_RETRY > 1:
# 				print 'Retrying in 3 seconds...'
# 				MAX_RETRY -= 1
# 				time.sleep(3)
# 				return get_interval(user, db, station)
# 			else:
# 				print 'false 1'
# 				return False
# 		if is_json(response.text):
# 			if json.loads(response.text).has_key('ReturnDataSet'):
# 				retrec = json.loads(response.text)['ReturnDataSet']
# 				return retrec
# 			else:
# 				print MAX_RETRY
# 				if MAX_RETRY > 1:
# 					print 'Retrying in 3 seconds...'
# 					MAX_RETRY -= 1
# 					time.sleep(3)
# 					return get_interval(user, db, station)
# 				else:
# 					print 'false 2'
# 					return False
# 		else:
# 			if MAX_RETRY > 1:
# 				print 'Retrying in 3 seconds...'
# 				MAX_RETRY -= 1
# 				time.sleep(3)
# 				return get_interval(user, db, station)
# 			else:
# 				print 'false 3'
# 				return False
# 	else:
# 		print 'dg code missing'

def get_minmax(station):
	MAX_RETRY = 3

	path = '/data/'+station
	headers = make_headers('GET', path)
	url = 'https://api.fieldclimate.com'

	while MAX_RETRY > 1:
		MAX_RETRY -= 1
		try:
			response = requests.get(url + path, headers=headers, verify=False) # very=false: this needs to be fixed
		except requests.exceptions.RequestException as e:
			print e 
			print 'Retrying in 3 seconds...'
			time.sleep(3)
			continue
		if response.status_code != 200:
			print 'Server returned http ', response.status_code
			print 'Retrying in 3 seconds...'
			time.sleep(3)
			continue
		else:
			print response.text
			return json.loads(response.text)






def get_interval(user, db, station):
    from visualizer.models import AppUser

    print 'getting measurment interval ...'
    global MAX_RETRY
    fc_acc = AppUser.objects.get(user=user)
    if db == 'fc':
		try:
			response = requests.post("http://www.fieldclimate.com/api/CIDIStationConfig2/Get",
		 	data={"user_name": fc_acc.fc_username, "user_passw" : fc_acc.fc_password, "station_name": station})
		 	print 'in get_interval ', response.status_code
		 	print response.text
		except requests.exceptions.RequestException as e:
			print e
			if MAX_RETRY > 1:
				print 'Retrying in 3 seconds...'
				MAX_RETRY -= 1
				time.sleep(3)
				return get_interval(user, db, station)
			else:
				return 0

		if is_json(response.text):
			if json.loads(response.text).has_key('ReturnDataSet'):
				retrec = json.loads(response.text)['ReturnDataSet']
				return retrec
			else:
				if MAX_RETRY > 1:
					print 'Retrying in 3 seconds...'
					MAX_RETRY -= 1
					time.sleep(3)
					return get_interval(user, db, station)
				else:
					return 0	
		else:
			if MAX_RETRY > 1:
				print 'Retrying in 3 seconds...'
				MAX_RETRY -= 1
				time.sleep(3)
				return get_interval(user, db, station)
			else:
				return False


# def get_sensor_lst(station):
# 	print 'getting sensor list'
# 	from visualizer.models import AppUser, Stations
# 	try:
# 		user = Stations.objects.filter(station=station)[0].user
# 	except IndexError as e:
# 		print e
# 		print 'IndexError'
# 		return
# 	print 'getting station sensors ...'
# 	global MAX_RETRY
# 	fc_acc = AppUser.objects.get(user=user)
# 	try:
# 		response = requests.post("http://www.fieldclimate.com/api/CIDIStationSensors/Get",
# 	 	data={"user_name": fc_acc.fc_username, "user_passw" : fc_acc.fc_password, "station_name": station})
# 	 	print 'in get_interval ', response.status_code
# 	 	print response.text
# 	except requests.exceptions.RequestException as e:
# 		print e
# 		if MAX_RETRY > 1:
# 			print 'Retrying in 3 seconds...'
# 			MAX_RETRY -= 1
# 			time.sleep(3)
# 			return get_sensor_lst(user, station)
# 		else:
# 			return 0

# 	if is_json(response.text):
# 		if json.loads(response.text).has_key('ReturnDataSet'):
# 			retrec = json.loads(response.text)['ReturnDataSet']
# 			return retrec
# 		else:
# 			if MAX_RETRY > 1:
# 				print 'Retrying in 3 seconds...'
# 				MAX_RETRY -= 1
# 				time.sleep(3)
# 				return get_sensor_lst(user, station)
# 			else:
# 				return 0	
# 	else:
# 		if MAX_RETRY > 1:
# 			print 'Retrying in 3 seconds...'
# 			MAX_RETRY -= 1
# 			time.sleep(3)
# 			return get_sensor_lst(user, station)
# 		else:
# 			return False

# {
#   "title": "User Station Insert Schema",
#   "type": "object",
#   "properties": {
#     "custom_name": {
#       "type": "string",
#       "pattern": "^[a-zA-Z\\s\\d]{0,35}$",
#       "description": "Only characters, numbers, spaces and max length 35"
#     }
#   },
#   "additionalProperties": False,
#   "description": "additionalProperties no new property can be created .... Data updated as whole object will overwrite whole set in database. Required property needs to be specified. Pattern is pattern in regex"
# }

#add station to admin user
# def add_fc_station(station, code):
# 	MAX_RETRY = 3
# 	path = '/station/'+station+'/'+code
# 	print path
# 	headers = make_headers('POST', path)
# 	url = 'https://api.fieldclimate.com'
# 	schema = json.dumps({"custom_name": "new station"})

# 	while MAX_RETRY > 1:
# 		MAX_RETRY -= 1
# 		try:
# 			response = requests.post(url + path, headers=headers, data=schema, verify=False) # very=false: this needs to be fixed
# 		except requests.exceptions.RequestException as e:
# 			print e 
# 			print 'Retrying in 3 seconds...'
# 			time.sleep(3)
# 			continue
# 		if response.status_code != 200:
# 			print 'Server returned http ', response.status_code
# 			print response.text
# 			print 'Retrying in 3 seconds...'
# 			time.sleep(3)
# 			continue
# 		else:
# 			print 'station successfully added.', json.loads(response.text)
# 			return json.loads(response.text)

def get_sensor_lst(station):
	MAX_RETRY = 3

	path = '/station/'+station+'/sensors'
	headers = make_headers('GET', path)
	url = 'https://api.fieldclimate.com'

	while MAX_RETRY > 1:
		MAX_RETRY -= 1
		try:
			response = requests.get(url + path, headers=headers, verify=False) # very=false: this needs to be fixed
		except requests.exceptions.RequestException as e:
			print e 
			print 'Retrying in 3 seconds...'
			time.sleep(3)
			continue
		if response.status_code != 200:
			print 'Server returned http ', response.status_code
			print 'Retrying in 3 seconds...'
			time.sleep(3)
			continue
		else:
			print 'sensor list retrieved from server'
			print type(json.loads(response.text))
			print 'number of sensors: ', len(json.loads(response.text))
			return json.loads(response.text)	



def get_row_count(user, db, station, dt_from, dt_to):
 	print 'Calculating row-count from input dates ...'

 	interval = 60
 	st_setting = get_interval(user, db, station)
 	if len(st_setting) > 0:
 		if st_setting[0].has_key('f_measure_int'):
 			interval = int(st_setting[0]['f_measure_int'])
 	
 	print 'interval: ', interval
 	if interval == 0:
 		interval = 60
 	rec_per_day = 60/interval

	diff = dt_to - dt_from
	if dt_from < dt_to:
		diff = dt_to - dt_from
	else:
		return 0

	if diff.days > 0:
		return int(diff.days * 24 * rec_per_day)
	else:
		return int((diff.seconds/60/60) * rec_per_day)

	return 0 


def get_unzip(file_name, user):
        from visualizer.models import Files
	print type(file_name)
	ziped_file = Files.objects.filter(user=user, file=file_name+'.kml')
	if ziped_file.exists():
		basename = os.path.basename(ziped_file[0].file.path)
		return settings.MEDIA_URL + basename
	kmz = ZipFile(Files.objects.filter(user=user, file=file_name)[0].file.path, 'r')
	kml = kmz.open('doc.kml', 'r')
	temp = tempfile.TemporaryFile()
	temp.write(kml.read())
	d_temp = File(temp)
	obj = Files(user=user, file=d_temp)
	obj.file.name = file_name+'.kml'
	obj.save()
	basename = os.path.basename(obj.file.path)
	return settings.MEDIA_URL + basename
	

def has_access(user, station):
	return True

def parse_date_http(date): # date in gmtime
	date = strftime("%a, %d %b %Y %H:%M:%S %Z", date)
	return date

def get_hmac(station, path):
	
	yesterday = parse_date("2017-11-13 09:00")
	# date_from = calendar.timegm((datetime.datetime.now() - timedelta(hours=12)).timetuple())
	date_from = calendar.timegm(yesterday.timetuple())
	date_to = calendar.timegm(datetime.datetime.now().timetuple())
	path = '/data/'+station+path
	print path

	headers = make_headers('GET', path)
	end_point = 'https://api.fieldclimate.com/v1'
	print end_point
	response = requests.get(end_point + path, headers=headers, verify=False) # very=false: this needs to be fixed

	print response.status_code
	# print response.text
	return json.dumps(response.text)

def make_headers(method, path, user=None):
	""" prepare http(s) headers according to
	fieldclimate requirements -- docs.fieldclimate.com """

	try:
		user = User.objects.get(username='admin') # remove is user not None
		app_user = AppUser.objects.get(user=user)
	except (User.DoesNotExist, AppUser.DoesNotExist) as e:
		print e
		return

	pub_key = str(app_user.pub_key) # why need to do str() ??
	prv_key = str(app_user.prv_key)
	date = parse_date_http(gmtime())
	# pub_key = '12c6204ef457e0bc67fa6dc3838da7fb62e18401'
	# prv_key = 'f3376eb3efacb577d333f8883774360c8f20491b'
	# app_user.update(pub_key=pub_key, prv_key=prv_key)
	content_to_sign = method + path + date + pub_key
	signature = hmac.new(prv_key, content_to_sign, sha256).hexdigest()
	auth_string = 'hmac ' + pub_key + ':' + signature
	headers = {
		'Accept': 'application/json',
		'Authorization': auth_string,
		'Date' : date
	}

	return headers








