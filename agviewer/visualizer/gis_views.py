# # -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.core import serializers
from visualizer.models import File, Feature, MapWidget, MapTileSource, Dashboard, FeatureStat, Widgets, Data
from django.contrib.auth.models import User
import json

def create_map_widget(request):
	""" Create new map widget
	"""
	try:
		options = json.loads(request.body)
		try:
			tile_source = MapTileSource.objects.get(name=options['tile_source'])
		except MapTileSource.DoesNotExist as e:
			print e
			tile_source = MapTileSource.objects.get(name='ArcGIS')
		url = options['tile_url']
		attribution = options['tile_attribution']
		zoom = options['zoom']
		latitude = options['center'][0]
		longitude = options['center'][1]
		dashboard = Dashboard.objects.get(user=request.user, active=True)
		widget = MapWidget(wid=options['wid'],user=request.user, name='', dashboard=dashboard, zoom=zoom\
			,latitude=latitude, longitude=longitude, tile_source=tile_source)
		widget.save()
		return HttpResponse(json.dumps({'success':True}))
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)

def get_map_widget_list(request):
	""" Get the list of all map widgets for this user's
		active dashboard
	"""
	try:
		dashboard = Dashboard.objects.get(user=request.user, active=True)
	except Dashboard.DoesNotExist as e:
		return HttpResponse(json.dumps({'message':'No active dashboards'}),status=500)
	try:
		map_widget_set = dashboard.mapwidget_set.all()
		map_widget_list = []
		for map_widget in map_widget_set:
			widget = {
				'wid': map_widget.wid,
				'name': map_widget.name,
				'center': [map_widget.latitude, map_widget.longitude],
				'tile_source': map_widget.tile_source.name,
				'tile_url': map_widget.tile_source.url,
				'tile_attribution': map_widget.tile_source.attribution, 
				'zoom': map_widget.zoom
			}
			map_widget_list.extend([widget])
		return HttpResponse(json.dumps(map_widget_list))
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)

def delete_map_widget(request):
	""" Delete a map widget
	"""
	try:
		params = json.loads(request.body)
		widget = MapWidget.objects.get(wid=params['wid'], user=request.user)
		widget.delete()
		return HttpResponse(json.dumps({'success': True}))
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)

def get_map_widget(request):
	""" Get a single map widget base on id
	"""
	try:
		params = json.loads(request.body)
		widget = MapWidget.objects.get(user=request.user, wid=params['wid'])
		widget_options = {
			'wid': widget.wid,
			'name': widget.name,
			'index': widget.index,
			'center': [widget.latitude, widget.longitude],
			'tile_source': widget.tile_source.name,
			'tile_url': widget.tile_source.url,
			'tile_attribution': widget.tile_source.attribution, 
			'zoom': widget.zoom
		}
		return HttpResponse(json.dumps(widget_options))
	except Exception, e:
		raise e

def change_map_widget(request):
	""" change map widget's options
	"""
	try:
		params = json.loads(request.body)
		widget = MapWidget.objects.filter(user=request.user, wid=params['wid'])
		tile_source = MapTileSource.objects.get(name=params['tile_source'])
		widget.update(index=params['index'], name=params['name'],\
			zoom=float(params['zoom']), latitude=float(params['lat']), longitude=float(params['long']), tile_source=tile_source)
		return HttpResponse(json.dumps({'success': True}))
	except Exception, e:
		raise e


def get_file_list(request):
	""" Retrieve user's list of files
	"""
	def get_object_props(obj):
		return {
			'fid': obj.fid.hex,
			'user': obj.user.username,
			'name': obj.file.name.split('/')[-1],
			'url': obj.file.url
		}

	try:
		files = File.objects.filter(user=request.user)
		file_list = [get_object_props(obj) for obj in files]
	except Exception as e:
		print e
	print file_list
	return HttpResponse(json.dumps(file_list))

def upload(request):
	""" Upload user file
	"""
	file = File(user=request.user, file=request.FILES['fileUpload'])
	file.save()
	print 'file saved'
	response = {
		'success': True,
		'url': file.file.url,
		'pk': file.fid.hex
	}
	return HttpResponse(json.dumps(response))

def remove(request):
	""" Remove a file
	"""
	file_ids = json.loads(request.body)
	try:
		for fid in file_ids:
			try:
				file = File.objects.get(fid=fid)
			except File.DoesNotExist:
				continue
			#delete file
			file.file.delete()
			#delete model object 
			file.delete()
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)
	return HttpResponse(json.dumps({'sucess':True}))

def save_feature(request):
	"""save map features to database
	"""
	try: 
		data = json.loads(request.body)
		print data
		widget = MapWidget.objects.get(wid=data['widget'])
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}), status=500)
	
	try:
		feature = Feature(name=data['feature']['properties']['name'],\
			geom_type=data['feature']['geometry']['type'], widget=widget, feature=data['feature'])
		feature.save()
	except Exception as e:
		raise e
	return HttpResponse(json.dumps({'fid':feature.fid.hex}))


def get_feature_list(request):
	""" Get list of features for a specific map
	"""
	try:
		params = json.loads(request.body)
		feature_set = MapWidget.objects.get(wid=params['wid']).feature_set.all()
		if feature_set.exists():
			feature_list = []
			for feature in feature_set:
				feature_dict = feature.feature
				#insert db given id
				feature_dict.update({"id": feature.fid.hex})
				feature_list.extend([feature_dict])
			response = {
				"type" : "FeatureCollection",
				"features" : feature_list
			}
			return HttpResponse(json.dumps(response))
		else:
			response = {
				"type" : "FeatureCollection",
				"features" : []
			}
			return HttpResponse(json.dumps(response))
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)

def create_feature_stat(params):
	""" Create stat calculations for a feature
	"""
	try:
		print params
		user = User.objects.get(username=params['user'])
		feature = Feature.objects.get(fid=params['feature_id'])
		stat_type = params['type']
		if stat_type == 'p':
			widget = Widgets.objects.get(widget_id=params['widget'][0], user=user)
			widget_data = widget.widget
			if widget_data['data']['paw'] is not None:
				paw_graphs = widget_data['data']['paw']['value']
				paw_values = []
				for graph in paw_graphs:
					paw_values.extend([graph[-1]['value']])
				if len(paw_values) > 0:
					try:
						value = round(sum(paw_values)/len(paw_values))
						feature_stat = FeatureStat(feature=feature, widget=widget, stat_type=stat_type, value=value)
						feature_stat.save()
						response = {
							'fsid': feature_stat.fsid.hex,
							'type': feature_stat.stat_type,
							'feature_name': feature_stat.feature.name,
							'feature_id': feature_stat.feature.fid.hex,
							'value': feature_stat.value
						}
						return {'response': response, 'status':200}
					except Exception as e:
						return {'response': {'message':e.message + 'here 1'}, 'status':500}
				else:
					return {'response': {'message':'No PAW graphs found.'}, 'status':500}
			else:
				return {'response': {'message':'No PAW calculation found.'}, 'status':500}
		else:
			data = Data.objects.get(id=params['new_data_id'])
			value = data.value
			feature_stat = FeatureStat(feature=feature, data=data, stat_type=stat_type, value=value)
			feature_stat.save()
			response = {
				'fsid': feature_stat.fsid.hex,
				'type': feature_stat.stat_type,
				'feature_name': feature_stat.feature.name,
				'feature_id': feature_stat.feature.fid.hex,
				'value': feature_stat.value
			}
			return {'response': response, 'status':200}
	except Exception as e:
		return {'response': {'message':e.message + 'here 2'}, 'status':500}

def update_feature_stat(fid):
	""" Update stat calculations for a feature
	"""
	try:
		feature = Feature.objects.get(fid=fid)
		featurestat_set = feature.featurestat_set.all()
		for stat in featurestat_set:
			if stat.stat_type == 'p':
				widget = stat.widget
				widget_data = widget.widget
				if widget_data['data']['paw'] is not None:
					paw_graphs = widget_data['data']['paw']['value']
					paw_values = []
					for graph in paw_graphs:
						paw_values.extend([graph[-1]['value']])
					if len(paw_values) > 0:
						try:
							value = round(sum(paw_values)/len(paw_values))
							stat.value = value
							stat.save()
						except Exception as e:
							raise e
					else:
						continue
				else:
					continue
			else:
				value = stat.data.value
				stat.value = value
				stat.save()
		return True
	except Exception as e:
		raise e

def get_feature_stats(request):
	""" Get the list of feature stats for a specific feature
	"""
	try:
		params = json.loads(request.body)
		feature = Feature.objects.get(fid=params['fid'])
		# update stat before returning value
		update_feature_stat(feature.fid)

		feature_stat_set = feature.featurestat_set.all()
		response_data = {
			'paw': {},
			'stats': []
		}
		for stat in feature_stat_set:
			if stat.stat_type == 's':
				stat_dict = {
					'fsid': stat.fsid.hex,
					'fid': stat.feature.fid.hex,
					'data': stat.data.name,
					'widget': stat.data.widget.widget['title'],
					'value': stat.value
				}
				response_data['stats'].extend([stat_dict])
			else:
				stat_dict = {
					'fsid': stat.fsid.hex,
					'fid': stat.feature.fid.hex,
					'widget': stat.widget.widget['title'],
					'value': stat.value
				}
				response_data['paw'].update(stat_dict)
		print response_data
		return HttpResponse(json.dumps(response_data))
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)

def get_feature_stat_widgets(request):
	""" Get list of Chart or Stat widgets connected
		to a specific map widget feature.
	"""
	try:
		params = json.loads(request.body)
		feature = Feature.objects.get(fid=params['fid'])
		feature_stat_set = feature.featurestat_set.all()
		response_data = {
			'paw': [],
			'stats': []
		}
		for stat in feature_stat_set:
			if stat.stat_type == 's':
				response_data['stats'].extend([stat.data.id])
			else:
				response_data['paw'].extend([stat.widget.widget_id])
		return HttpResponse(json.dumps(response_data))
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)

def change_paw_feature_stat(request):
	""" Change PAW feature stat for a specific feature
	"""
	try:
		params = json.loads(request.body)
		params.update({'user':request.user.username, 'type':'p'})
		print params
		feature = Feature.objects.get(fid=params['feature_id'])
		featurestat_set = feature.featurestat_set.filter(stat_type='p')
		paw_stat = None
		if featurestat_set.exists():
			paw_stat = featurestat_set[0]

		if len(params['widget']) > 0:
			if paw_stat is not None:
				if paw_stat.widget.widget_id == params['widget']:
					return HttpResponse(json.loads({'message': 'PAW feature stat already exists.'}))
				else:
					paw_stat.delete()
			widget = Widgets.objects.get(widget_id=params['widget'][0], user=request.user)
			response = create_feature_stat(params)
			return HttpResponse(json.dumps(response['response']), status=response['status'])
		else:
			if paw_stat is not None:
				paw_stat.delete()
			return HttpResponse(json.dumps({'message': 'PAW feature stat deleted.'}))
	except Exception as e:
		return HttpResponse(json.dumps({'message':e.message}),status=500)
	return HttpResponse(json.dumps({'message':'Invalid params'}),status=500)

def change_feature_stat(request):
	""" Change PAW feature stat for a specific feature
	"""
	try:
		params = json.loads(request.body)
		params.update({'user':request.user.username, 'type':'s'})
		print params
		feature = Feature.objects.get(fid=params['feature_id'])
		featurestat_set = feature.featurestat_set.filter(stat_type='s')
		existing_data_ids = [stat.data.id for stat in featurestat_set]
		new_data_ids = params['data_ids']
		for stat in featurestat_set:
			if str(stat.data.id) not in new_data_ids:
				stat.delete()
		if len(new_data_ids) < 1:
			featurestat_set.delete()
			count = str(len(existing_data_ids) if existing_data_ids is not None else 0)
			return HttpResponse(json.dumps({'message': count +' feature stats deleted.'}))
		response_data = []
		for data in new_data_ids:
			params.update({'new_data_id': data})
			response = create_feature_stat(params)
			response_data.extend([response['response']])

		return HttpResponse(json.dumps(response_data))
	except Exception, e:
		raise e

def get_chart_widget_list(request):
	""" Get the list of user's chart widgets
	"""
	try:
		chart_widgets = Widgets.objects.filter(user=request.user, widget_type='main-chart')
		widget_list = []
		for widget in chart_widgets:
			widget_list.extend([{'value': widget.widget_id, 'text': widget.widget['title']}])
		return HttpResponse(json.dumps(widget_list))
	except Exception, e:
		raise e

def get_data_widget_list(request):
	""" Get the list of user's chart widgets
	"""
	try:
		datas = Data.objects.filter(user=request.user)
		data_list = []
		for data in datas:
			data_list.extend([{'value': data.id, 'text': data.name, 'widget': data.widget.widget['title']}])
		return HttpResponse(json.dumps(data_list))
	except Exception, e:
		raise e

def resize_map(request):
	""" Resize map widget panel
	"""
	try:
		params = json.loads(request.body)
		widget = MapWidget.objects.get(user=request.user, wid=params['wid'])
		expand = params['expand']
		widget.expand = expand
		widget.save()
		return HttpResponse(json.dumps({'expand': widget.expand}))
	except Exception, e:
		raise e



