from visualizer.models import StationData
def change_data(station):
	records = StationData.objects.filter(station_id=station)

	for record in records:

		data = record.data
		modified_data = {}
		for key, val in data.iteritems():
			if key == 'date':
				modified_data.update({key:val})
				continue
			else:
				try:
					key_parts = key.split('_')
					sensor_id = key_parts[0] + '_' + key_parts[-2] + '_' + key_parts[-1]
					modified_data.update({sensor_id: val})
				except IndexError as e:
					print key
					modified_data.update({key:val})

		record.data = modified_data
		# print modified_data
		record.save()

def update_data(data_id):
	from visualizer.models import Data

	try:
		data = Data.objects.get(id=data_id)
	except Data.DoesNotExist as e:
		print e
		return
	if data.sensor is None:
		return
	if data.sensor.split('-')[0] == 'dg':
		return
	sensor_parts = data.sensor.split('_')
	if sensor_parts == 'ETo[mm]':
		return

	if len(sensor_parts) < 4:
		return
	print sensor_parts
	new_sensor = sensor_parts[0] + '_' + sensor_parts[-2] + '_' + sensor_parts[-1]

	data.sensor = new_sensor
	data.save()
	print 'saved'



def update_widgets(widgets):
	from visualizer.models import Widgets
	print 'updating widgets ...'
	for widget in widgets:
		old_widget = widget.widget
		if widget.widget_type == 'stat':
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
									if len(sub_sensor_parts) < 4:
										continue
									channel = sub_sensor_parts[0]
									code = sub_sensor_parts[-2]
									aggr = sub_sensor_parts[-1]
									new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr 
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
								if len(sub_sensor_parts) < 4:
									continue
								channel = sub_sensor_parts[0]
								code = sub_sensor_parts[-2]
								aggr = sub_sensor_parts[-1]
								new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr
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
								if len(sub_sensor_parts) < 4:
									continue
								channel = sub_sensor_parts[0]
								code = sub_sensor_parts[-2]
								aggr = sub_sensor_parts[-1]
								new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr
								val['params']['sensors'][i] = new_sensor_code
								#iterate over paw values replace sensor code in at index 0
								for counter, value in enumerate(val['value']):
									try:
										if v == value[0]['sensor']:
											val['value'][counter][0]['sensor'] = new_sensor_code
									except KeyError as e:
										print e
										continue

						elif key in ['chilling_portions', 'degree_days', 'chilling_hours']:
							sensor_parts = val['params']['sensors'].split('-')
							db = sensor_parts[0]
							if db == 'dg':
								print 'decagon sensor skipped.'
								continue
							station = sensor_parts[1]
							sensor = sensor_parts[2]
							sub_sensor_parts = sensor.split('_')
							if len(sub_sensor_parts) < 4:
								continue
							channel = sub_sensor_parts[0]
							code = sub_sensor_parts[-2]
							aggr = sub_sensor_parts[-1]
							new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr
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
							if len(sub_sensor_parts) < 4:
								continue
							channel = sub_sensor_parts[0]
							code = sub_sensor_parts[-2]
							aggr = sub_sensor_parts[-1]
							new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr
							val['params']['rh'] = new_sensor_code

							sensor_parts = val['params']['temp'].split('-')
							db = sensor_parts[0]
							if db == 'dg':
								print 'decagon sensor skipped.'
								continue
							station = sensor_parts[1]
							sensor = sensor_parts[2]
							sub_sensor_parts = sensor.split('_')
							if len(sub_sensor_parts) < 4:
									continue
							channel = sub_sensor_parts[0]
							code = sub_sensor_parts[-2]
							aggr = sub_sensor_parts[-1]
							new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr
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
									if sensor is None:
										continue
									station = sensor_parts[1]
									sensor = sensor_parts[2]
									if sensor == 'ETo[mm]':
										continue
									sub_sensor_parts = sensor.split('_')
									if len(sub_sensor_parts) < 4:
										continue
									channel = sub_sensor_parts[0]
									code = sub_sensor_parts[-2]
									aggr = sub_sensor_parts[-1]
									new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr
									val['params']['labels'].update({new_sensor_code:v})
									del val['params']['labels'][i]
									for counter, value in enumerate(val['value']):
										try:
											if v == value[0]['sensor']:
												val['value'][counter][0]['label_id'] = new_sensor_code
										except (KeyError, IndexError) as e:
											print e
											continue
							for i, v in enumerate(val['params']['sensors']):
								if v is None:
									continue
								sensor_parts = v.split('-')
								db = sensor_parts[0]
								if db == 'dg':
									print 'decagon sensor skipped.'
									continue
								if sensor is None:
									continue
								station = sensor_parts[1]
								sensor = sensor_parts[2]
								if sensor == 'ETo[mm]':
									continue
								sub_sensor_parts = sensor.split('_')
								if len(sub_sensor_parts) < 4:
									continue
								channel = sub_sensor_parts[0]
								code = sub_sensor_parts[-2]
								aggr = sub_sensor_parts[-1]
								new_sensor_code = 'fc-' + station + '-' + channel + '_' + code + '_' + aggr
								val['params']['sensors'][i] = new_sensor_code
					except KeyError as e:
						print e
			old_widget['data'][key] = val
			print 'sensor list updated '
		widget_to_update = Widgets.objects.filter(widget_id=widget.widget_id, user=widget.user).update(widget=old_widget)
		print '1 widget updated', widget.widget_id

	