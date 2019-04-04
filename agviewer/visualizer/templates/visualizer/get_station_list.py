import json, requests



class sensors():


	name = "jrperez"
	password = "12345" 
	station = "0110282B"

	def get_sensors(self):

		response = requests.post("http://www.fieldclimate.com/api/index.php?action=CIDIStationList_GetStations",
		 data={"user_name": self.name, "user_passw" : self.password}) 

		res = json.loads(response.text)

		# test
		#print res['ReturnDataSet']['01102B79']['custom_name']

		for k, v in res['ReturnDataSet'].iteritems():
			print k, v['custom_name']

		return res['ReturnDataSet']




# if __name__ == '__main__':

# 	get_sensors = sensors().get_sensors();

# 	print get_sensors

	
sensors = sensors().get_sensors();



