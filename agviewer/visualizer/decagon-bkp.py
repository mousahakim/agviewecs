import xml.etree.ElementTree as ET
import requests, time, json, datetime
from models import DSensorList

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



def convert(raw, value):

	if value == '241':
		return 3.62*10**-4 * float(raw) - 0.554
	elif value == '253':
		return 4.24*10**-4 * float(raw) - 0.29
	elif value == '254':
		return 5.71*10**-4 * float(raw) - 0.376
	elif value == '252':
		return 8.50*10**-4 * float(raw) - 0.481
	elif value == '249':
		return 1.17*10**-9 * float(raw)**3 - 3.95*10**-6 * float(raw)**2 + 4.90*10**-3 * float(raw) - 1.92
	elif value == '125':
		return 1.09*10**-3 * float(raw) - 0.629
	elif value == '122':
		return


def parse_xml(user):

	xml_tree = ET.parse('data1.dxd')									
	root = xml_tree.getroot()

	#variables
	#root = ET.fromstring(get_xml())
	data_list = []
	raw_string = None
	#update list of sensors
	for element in root.iter('Device'):
		station_id = element.attrib['id']
		station_name = element.attrib['name']


	for element in root.iter('Port'):
		if not DSensorList.objects.filter(user=user, sensor_id=element.attrib['value']+element.attrib['number']).exists():
			sensor_list = {'station_id':station_id, 'station_name':station_name, 'sensor_id':element.attrib['value'], 'sensor_name':element.attrib['sensor'], 'port_no':element.attrib['number']}
			sensor = DSensorList(user=user, sensor_id=station_id+'-'+element.attrib['value']+'-'+element.attrib['number'], sensor_list=sensor_list)
			sensor.save()

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
				dic.update({element.attrib['value']+'_'+str(j): convert(line.split(',')[i], element.attrib['value'])})
				j += 1
			else:
				dic.update({element.attrib['value']: convert(line.split(',')[i], element.attrib['value'])})
			i +=1
		data_list.extend([json.dumps(dic, sort_keys=True)])

	return data_list








