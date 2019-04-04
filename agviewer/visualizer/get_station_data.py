import json, requests



class sensors():


	name = "jrperez"
	password = "12345" 
	station = "0110282B"

	# test function for parsing json received from fieldclimate
	def get_sensors(self):

		response = requests.post("http://fieldclimate.com/api/index.php?action=CIDIStationData_GetLast",
		 data={"user_name": self.name, "user_passw" : self.password, "station_name": self.station, "row_count": 2}) 

		res = json.loads(response.text)

		# test
		print res['ReturnParams']
		j = 0
		for i, v in enumerate(res['ReturnDataSet']):
			for k, value in v.iteritems():
				print k+" -- Value: ", value
			j += 1
			print "----------------------------------------------------------------------------\n"
		print "Total Rows: ", j
		return res['ReturnDataSet']

	
	#get readings from all sensors for self.station
	def get_station_data(self):
		
		response = requests.post("http://fieldclimate.com/api/index.php?action=CIDIStationData_GetLast",
		 data={"user_name": self.name, "user_passw" : self.password, "station_name": self.station, "row_count": 2}) 

		res = json.loads(response.text)

		return res['ReturnDataSet']


	#extract ambient temp data from recordset return values in json format
	def get_ambient_temp(self):

		#dictionaries for storing sensor readings, min, max and average
		ambient_temp_set = []
		

		#record_name constants
		name_min = "sens_min_0_0"
		name_max = "sens_max_0_0"
		name_avg = "sens_aver_0_0"

		record_set = self.get_station_data()

		for i, v in enumerate(record_set):
			ambient_temp_set.extend([{"date_time": v['f_date'], "min": v[name_min], "avg": v[name_avg], "max": v[name_max]}])

		json_record_set = json.dumps(ambient_temp_set)
		print json_record_set
		return json_record_set

		



# if __name__ == '__main__':

# 	get_sensors = sensors().get_sensors();

# 	print get_sensors

	
# get_sensors = sensors().get_sensors();

get_data = sensors().get_ambient_temp();



