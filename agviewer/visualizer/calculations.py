from __future__ import division
from math import sqrt, exp, sin, cos, pi, atan, tan, log, floor
import datetime, time
from datetime import timedelta
from django.utils import timezone
from visualizer.utils import *
from visualizer.general import Alert


def satu_vap_pres(temp):

	result = 0.6108*exp((17.27*temp)/(temp+237.3))
	return round(result, 3)


def slope_satu_vap_pres(temp):

	result = (4098*(0.6108*exp((17.27*temp)/(temp+237.3)))) / ((temp+237.3)**2)
	return round(result, 3)


def mean_satu_vapo_pres(t_min, t_max): # t_avg = T

	t_max_k = t_max+273.16
	t_min_k = t_min+273.16

	e0_t_min = satu_vap_pres(t_min)
	e0_t_max = satu_vap_pres(t_max)

	result = (e0_t_max+e0_t_min)/2
	
	
	return round(result, 3)


def atmospheric_pres(altitude):

	result = 101.3*((293-0.0065*altitude)/293)**5.26
	
	return round(result, 1)

def actual_vap_pres_mean_rh(t_min, t_max, rh_mean):
	e0_t_min = satu_vap_pres(t_min)
	e0_t_max = satu_vap_pres(t_max)

	result = (rh_mean/100)*((e0_t_max+e0_t_min)/2)

	return result

def actual_vap_pres(t_min, t_max, rh_min, rh_max):
	e0_t_min = satu_vap_pres(t_min)
	e0_t_max = satu_vap_pres(t_max)


	result = (e0_t_min*((float(rh_max))/100)+e0_t_max*(float(rh_min)/100))/2

	return round(result, 3)


def solar_declination(day): # day = J
	
	result = 0.409*sin(((2*pi/365)*day)-1.39)

	return round(result, 3)


def sunset_hour_angle(lat_degrees, day): 
	
	x = 1 - tan(latitude(lat_degrees))**2 * tan(solar_declination(day=day))**2
	result = pi/2 - atan(-tan(latitude(lat_degrees)) * tan(solar_declination(day=day))/x**0.5)

	return round(result, 3)
	
# def latitude(lat_degrees): # may need to convert minutes to floating point 

# 	result = (pi/180)*lat_degrees

# 	return result
def latitude(lat_degrees): # may need to convert minutes to floating point 
	str_lat = str(round(lat_degrees, 2))
	lat_parts = str_lat.split('.')
	if len(lat_parts) > 1:
		decimal = float(lat_parts[-1])/60
	else:
		decimal = float('0.0')
	dec_degrees =float(lat_parts[0]) + decimal
	# print dec_degrees
	result = (pi/180)*dec_degrees
	return result

def invers_rel_distance(day):# day = J
	
	result = 1 + 0.033*cos((2*pi/365)*day)
	return round(result, 3)
	


def et_radiation(day, lat_degrees):

	SOLAR_CONST = 0.0820

	ird = invers_rel_distance(day=day)
	sha = sunset_hour_angle(lat_degrees=lat_degrees, day=day)
	sd = solar_declination(day=day)
	lat = latitude(lat_degrees=lat_degrees)
	intermediate = round((sha*sin(lat)*sin(sd)+cos(lat)*cos(sd)*sin(sha)), 2)
	result = ((24*60)/pi)*SOLAR_CONST*ird*intermediate

	return round(result, 1)


def clr_sky_rad(altitude, day, lat_degrees):

	ra = et_radiation(day=day, lat_degrees=lat_degrees)

	result = (0.75 + (2*10**-5)*altitude)*ra
	return round(result, 2)


def net_radiation(icmn_solar_rad, altitude, t_max, t_min, rh_min, rh_max, day, lat_degrees):

	GRASS_REF = 0.23
	SB_CONST = 4.903*10**-9 

	t_max_k = t_max+273.16 # get Tmin, K
	t_min_k = t_min+273.16 # get Tmax, K
	#icmn_solar_rad_mj = icmn_solar_rad*0.0864 # convert form w m^-2 to MJ m^-2 day^-1

	######
	net_shortwave_rad = (1 - GRASS_REF)*icmn_solar_rad
	# print 'net_shortwave_rad ', round(net_shortwave_rad, 2)

	######
	clr_sky = clr_sky_rad(altitude=altitude, day=day, lat_degrees=lat_degrees)
	actual_vap = actual_vap_pres(t_min=t_min, t_max=t_max, rh_min=rh_min, rh_max=rh_max)
	net_longwave_rad = SB_CONST*((t_max_k**4+t_min_k**4)/2)*(0.34-(0.14*sqrt(actual_vap)))*(1.35*(icmn_solar_rad/clr_sky)-0.35)

	# print 'net_longwave_rad ', round(net_longwave_rad, 2)



	#####

	result = round(net_shortwave_rad, 2) - round(net_longwave_rad, 2)
	return round(result, 3)


def psychrometric_const(altitude):

	a_pressure = atmospheric_pres(altitude)
	# print 'a_pressure ', a_pressure
	result = (0.665 * 10**-3)*a_pressure
	return result


def evapotranspiration(icmn_solar_rad, altitude, t_max, t_min, rh_min, rh_max, day, lat_degrees, t_avg, wind_speed):
	# print icmn_solar_rad, altitude, t_max, t_min, rh_min, rh_max, day, lat_degrees, t_avg, wind_speed
	net_rad = round(net_radiation(icmn_solar_rad, altitude, t_max, t_min, rh_min, rh_max, day, lat_degrees), 2)
	SOIL_HEAT_FLUX = 0.0
	mean_satu_vapo = mean_satu_vapo_pres(t_min, t_max) # is this average temp or max temp ??
	actual_vap = actual_vap_pres(t_min, t_max, rh_min, rh_max)
	vap_pres_deficit = mean_satu_vapo - actual_vap
	slope_satu_vap = slope_satu_vap_pres(t_avg)
	psychrometric = round(psychrometric_const(altitude), 2)

	# numerator = 0.408*slope_satu_vap*(net_rad - SOIL_HEAT_FLUX) + psychrometric*(900/(t_avg+273))*wind_speed*vap_pres_deficit
	# denominator = slope_satu_vap + psychrometric*(1+0.34*wind_speed)

	# print 'slope_satu_vap ', slope_satu_vap
	# print 'net_rad', net_rad
	# print 'psychrometric ', psychrometric
	# print 'wind_speed ', wind_speed
	# print 'mean_satu_vapo ', mean_satu_vapo
	# print 'actual_vap ', actual_vap
	# print 'vap_pres_deficit ', vap_pres_deficit

	p1 = (0.408*slope_satu_vap*net_rad) / (slope_satu_vap + psychrometric*(1+0.34*wind_speed))
	p2 = (psychrometric*(900/(t_avg+273))*wind_speed*vap_pres_deficit) / (slope_satu_vap + psychrometric*(1+0.34*wind_speed))
	# print 'numerator ', round(p1, 2)
	# print 'denominator ', round(p2, 2)
	# result = round(numerator, 2)/round(denominator, 2)
	result = round(p1, 2) + round(p2, 2)

	return round(result, 2)


def paw(fc, wp, paw_fields, sm_data, avg):
	return_set = {}
	avg_values = {}
	paw_set = []
	if avg:
		for key, value in sm_data.iteritems():
			for k, v in value.iteritems():
				if k in return_set:
					return_set[k] += float(v) if v is not None else 0
				else:
					return_set.update({k:float(v) if v is not None else 0})
		for k, v in return_set.iteritems():
			avg_values.update({k:(float(v)/float(len(sm_data)))})
		for k, v in avg_values.iteritems():
			if float(v) != 0:
				paw_val = (100+100*((float(v)-float(fc))/(int(fc)-int(wp))))
			else:
				paw_val = None

			paw_set.extend([{'date':k, 'value':paw_val}])
		return paw_set


	else:
		# print 'indidual paw case'
		for k, v in sm_data.iteritems():
			paw_lst = []
			for key, value in v.iteritems():
				if value is None:
					paw_lst.extend([{'date':key, 'value':value}])
					continue	
				if float(value) != 0:
					paw_val = (100+100*(float(value)-int(paw_fields[k]['fc']))/(int(paw_fields[k]['fc'])-int(paw_fields[k]['wp'])))
				else:
					paw_val = None

				paw_lst.extend([{'date':key, 'value':paw_val}])
			paw_lst_srt = sorted(paw_lst, key=lambda k: k['date'])
			if len(paw_lst_srt) > 0:
				paw_lst_srt[0].update({'sensor':k})
			paw_set.extend([paw_lst_srt])
		return paw_set
	return None 


def dew_point(temp, rh):
	if temp is None or rh is None:
		return None
	if temp == 0.0 or rh == 0.0:
		return None
	else:
		intermediate = (log(rh / 100) + ((17.27 * temp) / (237.3 + temp))) / 17.27
		result = (237.3 * intermediate) / (1 - intermediate)
		return result


def chill_portions(temp, prev):
	if temp is None:
		return prev
	E_ZERO = 4153.50
	E_ONE = 12888.80
	A_ZERO = 139500.00
	A_ONE  = 2567000000000000000.00
	SLP = 1.6
	TETMLT = 277
	AA = A_ZERO / A_ONE
	EE = E_ONE - E_ZERO
	temp_k = temp + 273
	ftmprt = SLP * TETMLT * (temp_k - TETMLT)/temp_k
	sr = exp(ftmprt)
	xi = round(sr/(1+sr), 2)
	xs = AA * exp(EE/temp_k)
	ak1 = A_ONE * exp(-E_ONE/temp_k)
	prev_inter_e = prev['inter_e']
	prev_xi = prev['xi']
	inter_s = None

	if prev_inter_e < 1:
		inter_s = prev_inter_e
	else:
		inter_s = prev_inter_e - prev_inter_e * prev_xi
	
	inter_e = (xs - (xs - inter_s) * exp(-ak1))
	delt = None
	
	if inter_e < 1:
		delt = 0
	else:
		delt = xi * inter_e

	prev_portions = prev['portions']
	# print {'xi':xi, 'inter_e':inter_e, 'delt':delt, 'portions':prev_portions+delt, 'accumulation':prev_portions+delt}
	return {'xi':xi, 'inter_e':inter_e, 'delt':delt, 'portions':prev_portions+delt, 'accumulation':prev_portions+delt}



def degree_days(temp, threshold):
	if temp is None:
		return 0
	dd = temp - threshold
	if dd >= 0:
		return dd
	else:
		return 0

def chill_hours(temp, threshold):
	if temp is None:
		return False
	if temp < threshold:
		return True
	return False

def saturation_ec(temp, vwc, ec, perm, offset, saturation, unit):
	print temp, vwc
	if temp is None:
		return None
	if vwc is None:
		return None
	if ec is None:
		ec = 0
	if perm is None:
		perm = 0
	temp = float(temp)
	vwc = float(vwc)
	ec = float(ec)
	perm = float(perm)
	offset = float(offset)
	devisor = 1
	if unit == 'msm':
		devisor = 100
	elif unit == 'mscm':
		devisor = 1
	elif unit == 'dsm':
		devisor = 1
	ep = 80.3 - 0.37*(temp - 20)
	sat_ec = abs((ep*ec/devisor)/(perm-offset))
	if sat_ec == 0 or saturation == 0:
		return 0
	sat = vwc / saturation* sat_ec
	return sat


def get_daily_avg(data):# data = list of dictionaries
	DAY = datetime.timedelta(hours=24)
	daily_avg = []
	start = parse_date(data[0]['date'])
	count = 0
	total = 0
	for it, rec in enumerate(data):
		if parse_date(rec['date']) < start + DAY:
		 	total += float(rec['value']) if rec['value'] is not None else 0
		 	count += 1
		 	if it == len(data)-1:
		 		value = total
		 		if total == 0:
		 			value = 0
		 		else:
		 			value = total/count
		 		daily_avg.extend([{'date':start.strftime('%Y-%m-%d'), 'value':value}])
		elif parse_date(rec['date']) >= start + DAY:
			if total == 0:
	 			value = 0
	 		else:
	 			value = total/count
		 	daily_avg.extend([{'date':start.strftime('%Y-%m-%d'), 'value':value}])
		 	start = parse_date(rec['date'])
		 	total = float(rec['value']) if rec['value'] is not None else 0
		 	count = 1
	return daily_avg # returns list of dictionaries

# def get_hourly_avg(data):# data = list of dictionaries
# 	HOUR = datetime.timedelta(hours=1)
# 	hourly_avg = []
# 	start = parse_date(data[0]['date']).replace(second=0, microsecond=0)
# 	count = 0
# 	total = 0
# 	for it, rec in enumerate(data):
# 		if parse_date(rec['date']).replace(second=0, microsecond=0) < start + HOUR:
# 		 	total += float(rec['value']) if rec['value'] is not None else 0
# 		 	count += 1
# 		 	if it == len(data)-1:
# 		 		value = total
# 		 		if total == 0:
# 		 			value = 0
# 		 		else:
# 		 			if count != 0:
# 			 			value = total/count
# 			 		else:
# 			 			value = total
# 		 		hourly_avg.extend([{'date':date_to_string(start), 'value':value}])
# 		elif parse_date(rec['date']).replace(second=0, microsecond=0) >= start + HOUR:
# 			if total == 0:
# 	 			value = 0
# 	 		else:
# 	 			if count != 0:
# 		 			value = total/count
# 		 		else:
# 		 			value = total
# 		 	hourly_avg.extend([{'date':date_to_string(start), 'value':value}])
# 		 	start = parse_date(rec['date']).replace(second=0, microsecond=0)
# 		 	total = float(rec['value']) if rec['value'] is not None else 0
# 		 	count = 0
# 	print hourly_avg
# 	return hourly_avg # returns list of dictionaries	



def get_daily_min(data):
	# print 'getting daily min'
	DAY = datetime.timedelta(hours=23, minutes=59)
	start = parse_date(data[0]['date'])
	daily_min = []
	temp_lst = []
	for count, rec in enumerate(data):
		if parse_date(rec['date']) < start + DAY:
			temp_lst.extend([float(rec['value']) if rec['value'] is not None else 0])
			if count == len(data)-1:
				daily_min.extend([{'date':start.strftime('%Y-%m-%d'), 'value':min(temp_lst)}])
		elif parse_date(rec['date']) >= start + DAY:
			daily_min.extend([{'date':start.strftime('%Y-%m-%d'), 'value':min(temp_lst)}])
			start = parse_date(rec['date'])
			temp_lst = [float(rec['value']) if rec['value'] is not None else 0]
	return daily_min			

def daily_min(data, reset_hr, reset_min):
	
	prev_rec = data[0]
	min_val = float(prev_rec['value'])
	daily_min_val = []
	for rec in data:
		hour = parse_date(rec['date']).hour
		minute = parse_date(rec['date']).minute
		if hour == reset_hr and minute == reset_min:
			daily_min_val.extend([{
				'date': parse_date(prev_rec['date']).strftime('%Y-%m-%d'),
				'value': min_val}])
			prev_rec = rec
			min_val = float(prev_rec['value'])
		value = float(rec['value'])
		if value < min_val:
			min_val = value
		prev_rec = rec
	if len(daily_min_val) == 0:
		daily_min_val.extend([{
			'date': parse_date(prev_rec['date']).strftime('%Y-%m-%d'),
			'value': min_val}])

	return daily_min_val

def daily_max(data, reset_hr, reset_min):
	
	prev_rec = data[0]
	max_val = float(prev_rec['value'])
	daily_max_val = []
	for rec in data:
		hour = parse_date(rec['date']).hour
		minute = parse_date(rec['date']).minute
		if hour == reset_hr and minute == reset_min:
			daily_max_val.extend([{
				'date': parse_date(prev_rec['date']).strftime('%Y-%m-%d'),
				'value': max_val}])
			prev_rec = rec
			max_val = float(prev_rec['value'])
		value = float(rec['value'])
		if value > max_val:
			max_val = value
		prev_rec = rec
	if len(daily_max_val) == 0:
		daily_max_val.extend([{
			'date': parse_date(prev_rec['date']).strftime('%Y-%m-%d'),
			'value': max_val}])

	return daily_max_val

def daily_avg(data, reset_hr, reset_min):
	
	prev_rec = data[0]
	max_val = None
	daily_avg_val = []
	count = 0
	total = 0
	for rec in data:
		hour = parse_date(rec['date']).hour
		minute = parse_date(rec['date']).minute
		if hour == reset_hr and minute == reset_min:
			try:
				daily_avg_val.extend([{
					'date': parse_date(prev_rec['date']).strftime('%Y-%m-%d'),
					'value': round(total/count, 2)}])
			except ZeroDivisionError as e:
				print e
			count = 0
			total = 0
			prev_rec = rec
		total += float(rec['value'])
		count += 1
		prev_rec = rec
	if len(daily_avg_val) == 0:
		try:
			daily_avg_val.extend([{
				'date': parse_date(prev_rec['date']).strftime('%Y-%m-%d'),
				'value': round(total/count, 2)}])
		except ZeroDivisionError as e:
			print e
	return daily_avg_val


def get_daily_max(data):
	# print 'getting daily max'
	DAY = datetime.timedelta(hours=23, minutes=59)
	start = parse_date(data[0]['date'])
	daily_min = []
	temp_lst = []
	for count, rec in enumerate(data):
		if parse_date(rec['date']) < start + DAY:
			temp_lst.extend([float(rec['value']) if rec['value'] is not None else 0])
			if count == len(data)-1:
				daily_min.extend([{'date':start.strftime('%Y-%m-%d'), 'value':max(temp_lst)}])
		elif parse_date(rec['date']) >= start + DAY:
			daily_min.extend([{'date':start.strftime('%Y-%m-%d'), 'value':max(temp_lst)}])
			start = parse_date(rec['date'])
			temp_lst = [float(rec['value'])  if rec['value'] is not None else 0]
	return daily_min

# def get_hourly_sum(data, multiplier):
# 	if len(data) < 1:
# 		return [{'date': '2016-01-01 8:00', 'value': 0}]
# 	hourly_sum = []
# 	prev = data[0]
# 	for i, rec in enumerate(data):
# 		if parse_date(rec['date']).minute == 0:
# 			prev_value = float(prev['value']) if prev['value'] is not None else 0
# 			rec_value = float(rec['value']) if rec['value'] is not None else 0
# 			hourly_sum.extend([{'date':rec['date'], 'value':(rec_value - prev_value)*multiplier}])
# 			prev = rec
# 	return hourly_sum

def get_hourly_sum(data, multiplier):
	if len(data) < 1:
		return [{'date': '2016-01-01 8:00', 'value': 0}]
	hourly_sum = []
	prev = data[0]
	for i, rec in enumerate(data):
		if parse_date(rec['date']).minute == 0:
			prev_value = float(prev['value']) if prev['value'] is not None else 0
			rec_value = float(rec['value']) if rec['value'] is not None else 0
			value = rec_value - prev_value if rec_value > prev_value else 0
			hourly_sum.extend([{'date':rec['date'], 'value':value*multiplier}])
			prev = rec
	return hourly_sum

def get_daily_sum(data, reset_hr, reset_min):
	if len(data) < 1:
		return [{'date': '2016-01-01 8:00', 'value': 0}]
	daily_sum = []
	interval_n = data[0]
	prev = interval_n
	for i, rec in enumerate(data):
		if parse_date(rec['date']).hour == reset_hr and parse_date(rec['date']).minute == reset_min:
			prev_value = float(prev['value']) if prev['value'] is not None else 0
			interval_n_value = float(interval_n['value']) if interval_n['value'] is not None else 0
			daily_sum.extend([{'date': prev['date'], 'value': prev_value - interval_n_value}])
			interval_n = prev
		prev = rec
	return daily_sum

def get_daily_sum_sr(data, reset_hr, reset_min):
	if len(data) < 1:
		return [{'date': '2016-01-01 8:00', 'value': 0}]
	daily_sum = []
	interval_n = data[0]
	prev = interval_n
	for i, rec in enumerate(data):
		if parse_date(rec['date']).hour == reset_hr and parse_date(rec['date']).minute == reset_min:
			prev_value = float(prev['value']) if prev['value'] is not None else 0
			interval_n_value = float(interval_n['value']) if interval_n['value'] is not None else 0
			daily_sum.extend([{'date': parse_date(prev['date']).strftime('%Y-%m-%d'), 'value': prev_value - interval_n_value}])
			interval_n = prev
		prev = rec
	return daily_sum

def get_sum_sr(data, reset_hr, reset_min, interval): # interval in hours
	if len(data) < 1:
		return [{'date': '2016-01-01 8:00', 'value': 0}]

	accu_per_interval = []
	interval_n = data[0]
	prev = interval_n
	accumulation = 0
	count = 0
	for i, rec in enumerate(data):
		count += 1
		accumulation += float(rec['value']) if rec['value'] is not None else 0
		if (parse_date(rec['date']).hour == reset_hr and parse_date(rec['date']).minute == reset_min) or\
		parse_date(rec['date']) - parse_date(interval_n['date']) >= timedelta(hours=interval):
			accumulation /= count if count !=0 else 1
			accu_per_interval.extend([{'date': parse_date(prev['date']).strftime('%Y-%m-%d'), 'value': accumulation}])
			accumulation = 0
			count = 0
			interval_n = rec
		prev = rec
	return accu_per_interval

def get_d_avg(data, reset_hr, reset_min, interval): # interval in hours
	if len(data) < 1:
		return [{'date': '2016-01-01 8:00', 'value': 0}]
	# print 'wind speed data'
	# print data
	accu_per_interval = []
	interval_n = data[0]
	prev = interval_n
	accumulation = 0
	count = 0
	for i, rec in enumerate(data):
		# print rec['date'], rec['value']
		# print accumulation
		if (parse_date(rec['date']).hour == reset_hr and parse_date(rec['date']).minute == reset_min) or\
		parse_date(rec['date']) - parse_date(interval_n['date']) >= timedelta(hours=interval):
			average = accumulation / count if count !=0 else 1
			accu_per_interval.extend([{'date': parse_date(prev['date']).strftime('%Y-%m-%d'), 'value': average}])
			# print {'date': parse_date(prev['date']).strftime('%Y-%m-%d'), 'value': average}
			accumulation = 0
			count = 0
			interval_n = rec
		count += 1
		accumulation += float(rec['value']) if rec['value'] is not None else 0
		prev = rec
	return accu_per_interval

def get_hourly_avg(data, reset_min, interval): # interval in hours
	if len(data) < 1:
		return [{'date': '2016-01-01 8:00', 'value': 0}]
	# print 'wind speed data'
	# print data
	accu_per_interval = []
	interval_n = data[0]
	prev = interval_n
	accumulation = 0
	count = 0
	for i, rec in enumerate(data):
		# print rec['date'], rec['value']
		# print accumulation
		if (parse_date(rec['date']).minute == reset_min) or\
		parse_date(rec['date']) - parse_date(interval_n['date']) >= timedelta(hours=interval):
			average = accumulation / count if count !=0 else accumulation
			accu_per_interval.extend([{'date': date_to_string(parse_date(prev['date']).replace(second=0, microsecond=0)), 'value': average}])
			# print {'date': parse_date(prev['date']).strftime('%Y-%m-%d'), 'value': average}
			accumulation = 0
			count = 0
			interval_n = rec
		count += 1
		accumulation += float(rec['value']) if rec['value'] is not None else 0
		prev = rec
	# print accu_per_interval
	return accu_per_interval

def get_sum(data, reset_hr, reset_min, interval): # interval in hours
	if len(data) < 1:
		return [{'date': '2016-01-01 8:00', 'value': 0}]

	accu_per_interval = []
	interval_n = data[0]
	prev = interval_n
	accumulation = 0
	for i, rec in enumerate(data):
		accumulation += float(rec['value']) if rec['value'] is not None else 0
		if (parse_date(rec['date']).hour == reset_hr and parse_date(rec['date']).minute == reset_min) or\
		parse_date(rec['date']) - parse_date(interval_n['date']) >= timedelta(hours=interval):
			accu_per_interval.extend([{'date': prev['date'], 'value': accumulation}])
			accumulation = 0
			interval_n = rec
		prev = rec
	return accu_per_interval

