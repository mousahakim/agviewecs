from __future__ import division
import xml.etree.ElementTree as ET
import requests, time, json, datetime
from models import DSensorList, DStationList
from math import exp, log

def get_xml():

	email = 'pzorzano@morph2ola.com'
	userpass = 'ceda-ruag'
	deviceid = '5G0C1745'
	devicepass = 'kiacu-ithia'
	
	params = {'email': email, 'userpass': userpass, 'deviceid': deviceid, 'devicepass': devicepass, 'report': 1, 'mrid': 3972, 'User-Agent': 'AgViewer_1.0' }
	url = 'http://api.ech2odata.com/morph2ola/dxd.cgi'
	
	res = requests.post(url, data=params)

	file = open('data1.dxd', 'w')
	file.write(res.text)
	print 'file written'
	return res.text

def decatime(seconds):
	DIFF = 946684800
	return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(seconds)+DIFF))

def dayofyear(date_string):
	frmt = '%Y-%m-%d %H:%M:%S'
	return datetime.datetime.strptime(date_string, frmt).timetuple().tm_yday

def parse_date(date_string):
	frmt = '%Y-%m-%d %H:%M:%S'
	return datetime.datetime.strptime(date_string, frmt)



def convert_sca(value, code, extract, unit=None):
	# print code, extract
	if code in ['64','65', '66', '67', '68']:
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		t_raw = rshift(value, 1) & 32767#
		if extract == 'body':
			t_raw = rshift(value, 16) & 65535#
		return (t_raw - 5000) / 100
	elif code == '95':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		if extract == 'direction':
			d_raw = rshift(value, 1) & 511#
			return d_raw
		elif extract == 'speed':
			s_raw = rshift(value, 10) & 4095#
			return s_raw
		elif extract in ['gusts', 'gust']:
			g_raw = rshift(value, 22) & 511
			return g_raw
		elif extract == 'temp':
			if g_raw <= 900:
				temp = (g_raw - 400) / 10 #
			else: 
				temp = ((900 + 5 * (g_raw - 900)) - 400 ) / 10 #
			return temp

	elif code == '101':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)

		dept_raw = value & 4095 #
		t_raw = rshift(value, 22)
		ec_raw = rshift(value, 12) & 1023 #

		if extract == 'dept':
			return dept_raw #* (103.3/506.7) 
		elif extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10 #
			elif t_raw > 900:
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #
		elif extract == 'ec':
			return (10**(ec_raw/190)) / 1000
		else:
			return dept_raw

	elif code == '105' or code == '106':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)

		dept_raw = value & 8191 #
		t_raw = rshift(value, 23)
		ec_raw = rshift(value, 13) & 511 #


		if extract == 'temp':
			if t_raw <= 10:
				return t_raw - 11
			else:
				return (t_raw - 20)/10
		elif extract == 'ec':
			return 10**(ec_raw/190) / 1000

		else:
			if dept_raw <= 5099:
				return dept_raw
			else:
				return (dept_raw - 5100) * 2 + 5100

	elif code == '110':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		irradiance_532_raw = rshift(value, 1) & 2047#
		irradiance_570_raw = rshift(value, 12) & 2047#
		# orientation = rshift(value, 23) & 3#
		variable_a_raw  = rshift(value, 25) & 63#
		variable_a = 100 / variable_a_raw
		if variable_a == 1:
			variable_a = 0.98
		irradiance_532 = 10**(irradiance_532_raw/480)/10000#
		irradiance_570 = 10**(irradiance_570_raw/480)/10000#
		pri = None
		if irradiance_532 == 0 or irradiance_570 == 0\
		or irradiance_532 == 2047 or irradiance_570 == 2047:
			return pri
		pri = (variable_a*irradiance_532 - irradiance_570)/(variable_a*irradiance_532+irradiance_570)
		return pri
	elif code == '111':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		irradiance_532_raw = rshift(value, 1) & 2047#
		irradiance_570_raw = rshift(value, 12) & 2047#
		orientation = rshift(value, 23) & 3#
		#up-facing orientation
		irradiance_532 = irradiance_532_raw/1000#
		irradiance_570 = irradiance_570_raw/1000#
		#down-facing orientation
		if orientation == 1:
			irradiance_532 = 10**(irradiance_532_raw/480)/10000#
			irradiance_570 = 10**(irradiance_570_raw/480)/10000#
		variable_a = None
		if irradiance_532 == 0 or irradiance_570 == 0\
		or irradiance_532 == 2047 or irradiance_570 == 2047:
			return variable_a
		variable_a = irradiance_570/irradiance_532
		return variable_a
	elif code == '114':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		red_raw = rshift(value, 1) & 2047#
		nir_raw = rshift(value, 12) & 2047#
		orientation = rshift(value, 23) & 3#
		variable_a_raw  = rshift(value, 25) & 63#
		variable_a = 100 / variable_a_raw
		if variable_a == 1:
			variable_a = 1.86
		red = 10**(red_raw/480)/10000#
		nir = 10**(nir_raw/480)/10000#
		ndvi = None
		if red == 0 or nir == 0:
			return ndvi
		ndvi = (variable_a*nir - red)/(variable_a*nir+red)
		return ndvi
	#LWS leaf wetness

	elif code == '220':

		if value is None:
			return None

		value = int(value)

		if value == 0:
			return 0

		psig_raw = rshift(value, 1) & 32767
		minutes_raw = rshift(value, 16) & 32767

		if extract == 'pressure':
			return (100 * ((psig_raw * (3000/4096)) - 500)/2500)*0.069
		if extract == 'minutes':
			return minutes_raw

		return (100 * ((psig_raw * (3000/4096)) - 500)/2500)*0.0691

	elif code == '222':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		counts = rshift(value, 22) & 1023#
		return counts
	elif code == '115':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		red_raw = rshift(value, 1) & 2047#
		nir_raw = rshift(value, 12) & 2047#
		orientation = rshift(value, 23) & 3#
		#up-facing orientation
		red = red_raw/1000#
		nir = nir_raw/1000#
		#down-facing orientation
		if orientation == 1:
			red = 10**(red_raw/480)/10000#
			nir = 10**(nir_raw/480)/10000#
		variable_a = None
		if red == 0 or nir == 0:
			return variable_a
		variable_a = red/nir
		return variable_a

	elif code == '238':
		value = float(value)
		return (1.895*10**-10 * value**3 - 1.222*10**-6 * value**2 + 2.855*10**-3 * value -2.154) * 100
	elif code == '241':
		if float(value) != 0.0:
			return 100*(3.62*10**-4 * float(value) - 0.554) #
		else:
			return 0.0

	elif code == '253':
		return 100*(4.24*10**-4 * float(value) - 0.29)

	elif code == '254':
		return 100*(5.71*10**-4 * float(value) - 0.376)

	elif code == '252':
		return 100*(8.50*10**-4 * float(value) - 0.481) #

	elif code == '248':
		return -exp**(6.43*10**-6 * value**2 - 3.10*10**-2 * value + 39.4) #

	elif code == '250':
		return round(value * (1500/4096) * 5.0, 2)

	elif code == '251':
		if value is None:
			return None
		if value == 0:
			return 0
		x = log((4095/value) - 1)
		return 25.01914 + x * (-22.8437 + x * (1.532076 + (-0.08372 * x )))

	elif code == '255':
		value = int(value)
		wp_raw = value & 65535#
		t_raw = rshift(value, 16) & 1023
		if extract == 'wp': # water potential
			return (10**(0.0001*wp_raw)) / -10.20408 #
		elif extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10 #
			elif t_raw > 900:
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #

	elif code == '249':
		return 100*(1.17*10**-9 * value**3 - 3.95*10**-6 * value**2 + 4.90*10**-3 * value - 1.92)

	elif code == '119':
		value = int(value)
		vwc_raw = value & 4095 #
		t_raw = rshift(value, 22)
		ec_raw = rshift(value, 12) & 1023 #
		if extract == 'moist':
			ea = vwc_raw / 50
			return 100*(5.89*10**-6 * ea**3 - 7.62*10**-4 * ea**2 + 3.67*10**-2 * ea - 7.53*10**-2) #
		elif extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10 #
			elif t_raw > 900:
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #
		elif extract == 'ec':
			return 10**(ec_raw/215) /1000 #
		elif extract == 'perm':
			return vwc_raw / 50
	elif code == '120':
		if value is None:
			return None
		value = int(value)
		t_raw = rshift(value, 22)
		vwc_raw = value & 4094
		if extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10
			elif t_raw > 900: 
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10
		elif extract == 'moist':
			return 100*(3.44*10**-11 * vwc_raw**3 - 2.20*10**-7 * vwc_raw**2 + 5.84*10**-4 * vwc_raw - 5.3*10**-2)
	elif code == '121':
		value = int(value)
		wp_raw = value & 65535#
		t_raw = rshift(value, 16) & 1023
		if extract == 'wp': # water potential
			return (10**(0.0001*wp_raw)) / -10.20408 #
		elif extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10 #
			elif t_raw > 900:
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #

	elif code == '104' or code == '103':
		value = int(value)
		rc_raw = value & 4095 #
		t_raw = rshift(value, 22)
		ec_raw = rshift(value, 12) & 1023 #

		if t_raw <= 900:
			temp = (t_raw - 400) / 10 #
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #

		if extract == 'temp':
			return temp
		elif extract == 'ec':
			return 10**(ec_raw/215) /1000
		elif extract == 'rc':
			return 3.879*10**-4 * rc_raw - 0.6956
		else:
			return 10**(ec_raw/215) /1000
				
	elif code == '107':
		value = int(value)
		wp_raw = value & 65535#
		t_raw = rshift(value, 16) & 1023
		if extract == 'wp': # water potential
			return (10**(0.0001*wp_raw)) / -10.20408 #
		elif extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10 #
			elif t_raw > 900:
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #

	elif code == '108':
		value = int(value)
		wp_raw = value & 65535#
		t_raw = rshift(value, 16) & 1023
		if extract == 'wp': # water potential
			return (10**(0.0001*wp_raw)) / -10.20408 #
		elif extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10 #
			elif t_raw > 900:
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #

	elif code == '122':
		value = int(value)
		vwc_raw = value & 4095 #
		t_raw = rshift(value, 22)
		ec_raw = rshift(value, 12) & 1023 #

		if extract == 'moist':
			return 100*(3.44*10**-11 * vwc_raw**3 - 2.20*10**-7 * vwc_raw**2 + 5.84*10**-4 * vwc_raw - 5.3*10**-2) #
		elif extract == 'temp':
			if t_raw <= 900:
				return (t_raw - 400) / 10 #
			elif t_raw > 900:
				return ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #
		elif extract == 'ec':
			if ec_raw <= 700:
				return ec_raw / 100 #
			elif ec_raw > 700:
				return (700 + 5 * (ec_raw - 700)) / 100 #
		elif extract == 'perm':
				return vwc_raw / 50 #

	elif code == '159':
		value = int(value)
		t_raw = value & 4095 #
		rh_raw = rshift(value, 12) & 255 #
		vp_raw = rshift(value, 20) & 1023 #
		if extract == 'temp':
			return 0.040 * t_raw - 39.55 #
		elif extract == 'rh':
			return 0.01 * (-4.0 + (rh_raw * (0.648 - 0.00072 * rh_raw) + ((0.040*rh_raw-39.55) - 25.0) * (0.01 + 0.00128 * rh_raw))) #
		elif extract == 'vp':# vapor pressure
			return vp_raw / 75 #
	elif code == '223':
		return value # ask rodrigo.

	elif code == '221':
		print value
		value = int(value)
		return value
	elif code == '180': #flow meter
		value = int(value)
		#default multiplier
		return value * 3.785#
	elif code == '183': # flow meter
		value = int(value)
		#default multiplier
		return value * 3.785#

	elif code == '117':
		if extract == 'water_dept':
			if unit == 'mm':
				return value *(101.3/506.7)
			elif unit == 'ml':
				return (value/10) * 101.3 #
 			elif unit == '%': 
				return value/400 * 100 #
		elif extract == 'temp': 
			if value <= 900:
				return (value - 400) / 10 #
			elif value > 900:
				return ((900 + 5 * (value - 900)) - 400 ) / 10 #
		elif extract == 'ec': # electric conductivity
			return 10**(value/190) /1000

	elif code == '102':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		t_raw = rshift(value, 12) & 1023 #
		atm_raw = value & 4095 #
		rh_raw = rshift(value, 22)
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10
		if extract == 'temp':
			return temp
		elif extract == 'rh':
			rh = (rh_raw/100)/(0.611*exp((17.502*temp)/(240.97+temp)))
			return round(rh*100, 3)

	elif code == '112':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		t_raw = rshift(value, 16) & 1023 #
		vp_raw = value & 65535 #
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10
		if extract == 'temp':
			return temp
		elif extract == 'rh':
			rh = (vp_raw/100)/(0.611*exp((17.502*temp)/(240.97+temp)))
			return round(rh*100, 3)

	elif code == '186':
		value = int(value)
		if extract == 'direction':
			direction_raw = value & 511
			return direction_raw
		elif extract == 'speed':
			speed_raw = rshift(value, 20) & 511
			return round(1.006 * speed_raw / 10, 1)
		elif extract == 'gusts':
			gusts_raw = rshift(value, 10) & 511	
			return round(1.006 * gusts_raw / 10, 1)

	return value


def convert(value, code):
	if code in ['64','65', '66', '67', '68']:
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		t_raw_target = rshift(value, 1) & 32767#
		# t_raw_body = rshift(value, 16) & 65535#
		t_target = (t_raw_target - 5000) / 100
		# t_body = (t_raw_target - 5000) / 100
		return {
			'Apogee Target Temp': t_target,
			# 'Apogee Body Temp': t_body
			}
	elif code == '95':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		# d_raw = rshift(value, 1) & 511#
		s_raw = rshift(value, 10) & 4095#
		# g_raw = rshift(value, 22) & 511
		# if g_raw <= 900:
		# 	temp = (g_raw - 400) / 10 #
		# else: 
		# 	temp = ((900 + 5 * (g_raw - 900)) - 400 ) / 10 #
		wind_speed = s_raw / 100
		if wind_speed > 40.94:
			wind_speed = None
		return {
			# 'DS-2 Sonic Anemometer Wind Direction': d_raw,
			'DS-2 Sonic Anemometer Wind Speed': wind_speed,
			# 'DS-2 Sonic Anemometer Wind Gusts': g_raw,
			# 'DS-2 Sonic Anemometer Temp': temp
		}

	elif code == '101':
		if value is None:
			return {
				'CDT/G3 Drain': None,
				'CDT/G3 Temp': None,
				'CDT/G3 EC': None
			}
		if value == 0:
			return {
				'CDT/G3 Drain': 0,
				'CDT/G3 Temp': 0,
				'CDT/G3 EC': 0
			}
		value = int(value)

		dept_raw = value & 4095 #
		t_raw = rshift(value, 22)
		ec_raw = rshift(value, 12) & 1023 #

		temp = None

		if t_raw <= 900:
			temp = (t_raw - 400) / 10 #
		elif t_raw > 900:
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #
		return {
			'CDT/G3 Drain': dept_raw,
			'CDT/G3 Temp': temp,
			'CDT/G3 EC': (10**(ec_raw/190)) / 1000
		}

	elif code == '105' or code == '106':
		if value is None:
			return {
				'CDT Dept': None,
				'CDT Temp': None,
				'CDT EC': None
			}
		if value == 0:
			return {
				'CDT Dept': 0,
				'CDT Temp': 0,
				'CDT EC': 0
			}
		value = int(value)

		dept_raw = value & 8191 #
		t_raw = rshift(value, 23)
		ec_raw = rshift(value, 13) & 511 #

		if t_raw <= 10:
			temp = t_raw - 11
		else:
			temp = (t_raw - 20)/10

		ec = 10**(ec_raw/190) / 1000

		if dept_raw <= 5099:
			water_dept = dept_raw
		else:
			water_dept = (dept_raw - 5100) * 2 + 5100


		return {
			'CDT Dept' : water_dept,
			'CDT Temp': temp,
			'CDT EC': ec
		}

	elif code == '110':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		irradiance_532_raw = rshift(value, 1) & 2047#
		irradiance_570_raw = rshift(value, 12) & 2047#
		# orientation = rshift(value, 23) & 3#
		variable_a_raw  = rshift(value, 25) & 63#
		variable_a = 100 / variable_a_raw
		if variable_a == 1:
			variable_a = 0.98
		irradiance_532 = 10**(irradiance_532_raw/480)/10000#
		irradiance_570 = 10**(irradiance_570_raw/480)/10000#
		pri = None
		if irradiance_532 == 0 or irradiance_570 == 0\
		or irradiance_532 == 2047 or irradiance_570 == 2047:
			return {'PRI': pri}
		pri = (variable_a*irradiance_532 - irradiance_570)/(variable_a*irradiance_532+irradiance_570)
		return {'PRI': PRI}
	elif code == '111':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		irradiance_532_raw = rshift(value, 1) & 2047#
		irradiance_570_raw = rshift(value, 12) & 2047#
		orientation = rshift(value, 23) & 3#
		#up-facing orientation
		irradiance_532 = irradiance_532_raw/1000#
		irradiance_570 = irradiance_570_raw/1000#
		#down-facing orientation
		if orientation == 1:
			irradiance_532 = 10**(irradiance_532_raw/480)/10000#
			irradiance_570 = 10**(irradiance_570_raw/480)/10000#
		variable_a = None
		if irradiance_532 == 0 or irradiance_570 == 0\
		or irradiance_532 == 2047 or irradiance_570 == 2047:
			return variable_a
		variable_a = irradiance_570/irradiance_532
		return {'PRI Variable_a': variable_a}
	elif code == '114':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		red_raw = rshift(value, 1) & 2047#
		nir_raw = rshift(value, 12) & 2047#
		orientation = rshift(value, 23) & 3#
		variable_a_raw  = rshift(value, 25) & 63#
		variable_a = 100 / variable_a_raw
		if variable_a == 1:
			variable_a = 1.86
		red = 10**(red_raw/480)/10000#
		nir = 10**(nir_raw/480)/10000#
		ndvi = None
		if red == 0 or nir == 0:
			return {'NDVI': ndvi}
		ndvi = (variable_a*nir - red)/(variable_a*nir+red)
		return {'NDVI': ndvi}
	elif code == '115':
		if value is None:
			return None
		if value == 0:
			return 0
		value = int(value)
		red_raw = rshift(value, 1) & 2047#
		nir_raw = rshift(value, 12) & 2047#
		orientation = rshift(value, 23) & 3#
		#up-facing orientation
		red = red_raw/1000#
		nir = nir_raw/1000#
		#down-facing orientation
		if orientation == 1:
			red = 10**(red_raw/480)/10000#
			nir = 10**(nir_raw/480)/10000#
		variable_a = None
		if red == 0 or nir == 0:
			return variable_a
		variable_a = red/nir
		return {'NDVI Variable_a': variable_a}
	elif code == '238':
		value = float(value)
		if value is None or value == 0:
			return value

		return {
			'Teros10 VWC': (1.895*10**-10 * value**3 - 1.222*10**-6 * value**2 + 2.855*10**-3 * value -2.154) * 100
		}
	elif code == '241':
		if float(value) != 0.0:
			return {'GS1 Moisture':100*(3.62*10**-4 * float(value) - 0.554)}
		else:
			return {'GS1 Moisture':0.0}
	elif code == '253':
		return {'EC-20 Soil Moist':100*(4.24*10**-4 * float(value) - 0.29)}
	elif code == '254':
		return {'EC-10 Soil Moist':100*(5.71*10**-4 * float(value) - 0.376)}
	elif code == '252':
		return {'EC-5 Soil Moist':100*(8.50*10**-4 * value - 0.481)}
	elif code == '248':
		return {'MPS-1 Water Potential':-exp**(6.43*10**-6 * value**2 - 3.10*10**-2 * value + 39.4)}
	elif code == '250':
		return {'PYR Solar Radiation':value * (1500/4096) * 5.0}
	elif code == '245':
		return {'QSO-S PAR':value * (1500/4096) * 5.0}
	elif code == '251':
		value = int(value)
		print 'int value', value
		if value is None:
			return {'RT-1 Temp':None}
		if value == 0:
			return {'RT-1 Temp':0}
		try:
			x = log((4095/value) - 1)
		except ValueError as e:
			print e, value
			return {'RT-1 Temp':None}
		return {'RT-1 Temp':25.01914 + x * (-22.8437 + x * (1.532076 + (-0.08372 * x )))}
		
	elif code == '249':
		return {'10HS Soil Moist':100*(1.17*10**-9 * value**3 - 3.95*10**-6 * value**2 + 4.90*10**-3 * value - 1.92)}
	elif code == '119':
		value = int(value)
		vwc_raw = value & 4095 #
		t_raw = rshift(value, 22)
		ec_raw = rshift(value, 12) & 1023 #

		if t_raw <= 900:
			temp = (t_raw - 400) / 10 #
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #
		ea = vwc_raw / 50 #

		return {
			'GS3 Moisture':100*(5.89*10**-6 * ea**3 - 7.62*10**-4 * ea**2 + 3.67*10**-2 * ea - 7.53*10**-2),
			'GS3 Temp': temp,
			'GS3 EC':10**(ec_raw/215) /1000}

	elif code == '121':
		value = int(value)
		wp_raw = value & 65535#
		t_raw = rshift(value, 16) & 1023
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10
		return {'MPS-2 Water Potential':10**(0.0001*wp_raw) / -10.20408, 'MPS-2 Temp': temp}

	elif code == '104' or code == '103':
		value = int(value)
		rc_raw = value & 4095 #
		t_raw = rshift(value, 22)
		ec_raw = rshift(value, 12) & 1023 #

		if t_raw <= 900:
			temp = (t_raw - 400) / 10 #
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10 #

		return {
			'Teros1x Rc':3.879*10**-4 * rc_raw - 0.6956,
			'Teros1x Temp': temp,
			'Teros1x EC':10**(ec_raw/215) /1000}

	elif code == '107':
		value = int(value)
		wp_raw = value & 65535#
		t_raw = rshift(value, 16) & 1023
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10
		return {'Teros21 Water Potential':(10**(0.0001*wp_raw)) / -10.20408, 'Teros21 Temp': temp}

	elif code == '108':
		value = int(value)
		wp_raw = value & 65535#
		t_raw = rshift(value, 16) & 1023
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10
		return {'MPS-6 Water Potential':(10**(0.0001*wp_raw)) / -10.20408, 'MPS-6 Temp': temp}

	elif code == '122':
		value = int(value)
		t_raw = rshift(value, 22)
		vwc_raw = value & 4095 ##
		ec_raw = rshift(value, 12) & 1023 ##


		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10

		if ec_raw <= 700:
			ec = ec_raw / 100 #
		elif ec_raw > 700:
			ec = (700 + 5 * (ec_raw - 700)) / 100

		return {
			'5TE Moisture':100*(3.44*10**-11 * vwc_raw**3 - 2.20*10**-7 * vwc_raw**2 + 5.84*10**-4 * vwc_raw - 5.3*10**-2),
			'5TE Temp': temp,
			'5TE EC': ec}
	
	elif code == '120':
		if value is None:
			return None
		value = int(value)
		t_raw = rshift(value, 22)
		vwc_raw = value & 4094
		print t_raw
		print vwc_raw
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		elif t_raw > 900: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10
		return {
			'5TM Moisture':100*(3.44*10**-11 * vwc_raw**3 - 2.20*10**-7 * vwc_raw**2 + 5.84*10**-4 * vwc_raw - 5.3*10**-2),
			'5TM Temp': temp}

	elif code == '159':
		value = int(value)
		t_raw = value & 4095 #
		rh_raw = rshift(value, 12) & 255 #
		vp_raw = rshift(value, 20) & 1023 #
		return {
			'EHT Temp':0.040 * t_raw - 39.55,
			'EHT RH':0.01 * (-4.0 + (rh_raw * (0.648 - 0.00072 * rh_raw) + ((0.040*rh_raw-39.55) - 25.0) * (0.01 + 0.00128 * rh_raw))),
			'EHT VP': vp_raw / 75}

	elif code == '220':

		if value is None:
			return {
				'PT100 Pressure': None,
				# 'PT100 Minutes': None
			}

		value = int(value)

		if value == 0:
			return {
				'PT100 Pressure': 0,
				# 'PT100 Minutes': 0
			}

		psig_raw = rshift(value, 1) & 32767
		minutes_raw = rshift(value, 16) & 32767

		return {
			'PT100 Pressure': (100 * ((psig_raw * (3000/4096)) - 500)/2500)*0.069,
			# 'PT100 Minutes': minutes_raw
		}

	elif code == '221':
		print value
		return {'PS-1': float(value)}

	elif code == '223':
		return {'G1 Drain Guage':value} # ask rodrigo.

	elif code == '180':
		value = int(value)
		return {'Flow Meter': value}
		
	elif code == '183': # flow meter
		value = int(value)
		return {'Flow Meter':value*3.785}#default multiplier
	elif code == '189':
		return {'ECRN 50 Precipitation':value}

	elif code == '117':
		if value <= 900:
			temp = (value - 400) / 10
		else: 
			temp = ((900 + 5 * (value - 900)) - 400 ) / 10

		return {'GS3 Water Dept': value *(101.3/506.7), 'GS3 Temp': temp, 'GS3 EC': 10**(value/190) /1000}

	elif code == '102':
		if value is None:
			return {'Vp4 Temp': None, 'Vp4 RH': None}
		if value == 0:
			{'Vp4 Temp': 0, 'Vp4 RH': 0}
		value = int(value)
		t_raw = rshift(value, 12) & 1023 #
		atm_raw = value & 4095 #
		rh_raw = rshift(value, 22)
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10	

		rh = (rh_raw/100)/(0.611*exp((17.502*temp)/(240.97+temp)))
		return {'Vp4 Temp': temp, 'Vp4 RH': rh * 100} # has to be in %

	elif code == '112':
		if value is None:
			return {'Vp3 Temp': None, 'Vp3 RH': None}
		if value == 0:
			{'Vp3 Temp': 0, 'Vp3 RH': 0}
		value = int(value)
		t_raw = rshift(value, 16) & 1023 #
		vp_raw = value & 65535 #
		if t_raw <= 900:
			temp = (t_raw - 400) / 10
		else: 
			temp = ((900 + 5 * (t_raw - 900)) - 400 ) / 10	

		rh = (vp_raw/100)/(0.611*exp((17.502*temp)/(240.97+temp)))
		return {'Vp3 Temp': temp, 'Vp3 RH': rh * 100} # has to be in %	

	elif code == '186':
		value = int(value)
		direction_raw = value & 511
		speed_raw = rshift(value, 20) & 511
		gusts_raw = rshift(value, 10) & 511

		speed = 1.006 * speed_raw / 10
		gusts = 1.006 * gusts_raw / 10

		return {
			'Wind Speed': speed,
			# 'Wind Direction': direction_raw,
			'Wind Gusts': gusts}

		# if extract == 'water_dept':
		# 	if unit == 'mm':
		# 		return value *(101.3/506.7)
		# 	elif unit == 'ml':
		# 		return (value/10) * 101.3 #
 	# 		elif unit == '%': 
		# 		return value/400 * 100 #
		# elif extract == 'temp': 
		# 	if value <= 900:
		# 		return (value - 400) / 10 #
		# 	elif value > 900:
		# 		return ((900 + 5 * (value - 900)) - 400 ) / 10 #
		# elif extract == 'ec': # electric conductivity
		# 	return 10**(value/190) /1000
	return {'unknown sensor': value}

def rshift(value, bits):
	return int(value) >> bits

def station_from_xml(xml):

	#variables
	root = ET.fromstring(xml)
	sensors = {}
	#update list of sensors
	for element in root.iter('Device'):
		station_id = element.attrib['id']
		station_name = element.attrib['name']

	for element in root.iter('Port'):
		sensors.update({element.attrib['value']+'-'+element.attrib['number']: element.attrib['sensor']+ ' ['+element.attrib['number']+']'}) # sensor list for Stations model

	return {'station': station_id, 'name': station_name, 'sensors':sensors}







