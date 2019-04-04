from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import AuthenticationForm
from django.contrib.auth import logout
from django.forms.widgets import PasswordInput, TextInput
from django import forms
from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST
from .forms import FileUploadForm
import requests, json, time, os, sys, datetime, uuid
from models import AppUser, Files, Alerts, AlertEvents, Settings, Widgets, Dashboard, Data, MapWidget, MapTileSource
from get_records import *
from .general import Alert
from django.db import IntegrityError
from utils import date_to_string
# Create your views here.

@login_required
def index(request):
	
	chart_widgets = Widgets.objects.filter(widget_type='main-chart', user=request.user)
	stat_widgets = Widgets.objects.filter(widget_type='stat', user=request.user)
	map_widgets = MapWidget.objects.filter(user=request.user)
	fc_stations = Stations.objects.filter(user=request.user, database='fc')
	dg_stations = Stations.objects.filter(user=request.user, database='dg')
	tile_sources = MapTileSource.objects.all()
	dashboards = Dashboard.objects.filter(user=request.user)
	dash = request.GET.get('dashboard')
	app_user = AppUser.objects.get(user=request.user)
	if dash is None:
		try:
			activedash = Dashboard.objects.get(user=request.user, active=True)
			chart_widgets = chart_widgets.filter(dashboard=activedash)
			stat_widgets = stat_widgets.filter(dashboard=activedash)
			map_widgets = map_widgets.filter(dashboard=activedash)
		except Dashboard.DoesNotExist as e:
			print e
		
		return render(request,'index.html', {
			'name': request.user.first_name,
			'chart_widgets': chart_widgets,
			'stat_widgets': stat_widgets,
			'map_widgets' : map_widgets, 
			'fc_stations': fc_stations,
			'dg_stations': dg_stations, 
			'dashboards': dashboards, 
			'app_user': app_user,
			'tile_sources': tile_sources

		})
	
	try:
		Dashboard.objects.filter(user=request.user).update(active=False)
	except:
		print 'dashboards update failed'
	
	try:
		activedash = Dashboard.objects.get(user=request.user, uid=dash)
		#change active dash
		activedash.active = True
		activedash.save()
	except Dashboard.DoesNotExist as e:
		print e
		activedash = Dashboard.objects.filter(user=request.user)[0]


	chart_widgets = chart_widgets.filter(dashboard=activedash)
	stat_widgets = stat_widgets.filter(dashboard=activedash)
	map_widgets = map_widgets.filter(dashboard=activedash)

	# t1 = datetime.datetime.now()
	# data_sensors = {}
	# for station in fc_stations:
	# 	data = StationData.objects.filter(station_id=station.station)
	# 	if data.exists():
	# 		data_sensors.update({station.station:[k for k, v in data.last().data.iteritems() if v != None]})
	# print (datetime.datetime.now() - t1).seconds


	return render(request,'index.html', {
		'name': request.user.first_name,
		'chart_widgets': chart_widgets,
		'stat_widgets': stat_widgets, 
		'map_widgets' : map_widgets, 
		'fc_stations': fc_stations,
		'dg_stations': dg_stations, 
		'dashboards': dashboards,
		'app_user': app_user,
		'tile_sources': tile_sources

		})	


@login_required
def gis_view(request):
	form = FileUploadForm()
	fc_stations = Stations.objects.filter(user=request.user, database='fc')
	dg_stations = Stations.objects.filter(user=request.user, database='dg')
	alerts = Alerts.objects.filter(user=request.user)
	dashboards = Dashboard.objects.filter(user=request.user)

	return render(request,'gis.html', {
			'name': request.user.first_name,
			'fc_stations': fc_stations,
			'dg_stations': dg_stations, 
			'alerts': alerts,
			'dashboards': dashboards,
			'form':form
			})

class ANAuthenticationForm(AuthenticationForm):

	username = forms.CharField(widget=TextInput(attrs={'placeholder': 'Username', 'class':'form-control'}))
	password = forms.CharField(widget=PasswordInput(attrs={'placeholder':'Password', 'class':'form-control'}))


def logout_view(request):
	logout(request)


@login_required
def get_widgets(request):
	widget_dict = load_widgets(request.user)
	
	return HttpResponse(json.dumps(widget_dict))

@login_required
def widget_lst(request):
	widgets = Widgets.objects.filter(user=request.user)
	widget_lst = [widget.widget_id for widget in widgets if widget.widget_type !='stat']
	return HttpResponse(json.dumps(widget_lst))

@login_required
def widget(request):
	if request.is_ajax():
		if request.method == 'POST':
			data = json.loads(request.body) # {widget: '<widget_id>'}
			widget = Widgets.objects.filter(user=request.user, widget_id=data['widget'])
			#widget_dict = {}
			if widget.exists():
				date_range = parse_date(widget[0].widget['data']['range']['to']) - parse_date(widget[0].widget['data']['range']['from'])
				today = datetime.datetime.now() - (HOUR * 2)
				date_from = today - date_range
				new_widget = widget[0].widget
				new_widget['data']['range']['to'] = date_to_string(today)
				new_widget['data']['range']['from'] = date_to_string(date_from)
				update_widget = set_widget(new_widget, request.user)
				return HttpResponse(json.dumps({'widget':update_widget}))

@login_required
def changedaterange(request):
	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Non-ajax requests not allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)
	
	print request.body

	params = json.loads(request.body)

	widgetid = params['widgetID']
	try:
		widget = Widgets.objects.get(user=request.user, widget_id=widgetid)
	except Widgets.DoesNotExist as e:
		print e
		#return 404
		responsedata = {
			'success': False,
			'message': 'Widget not found.'
		}
		return HttpResponse(json.dumps(responsedata), status=404)


	if widget.widget_type == 'stat':
		#return bad request
		responsedata = {
			'success': False,
			'message': 'Bad request.'
		}
		return HttpResponse(json.dumps(responsedata), status=400)

	datefrom = params['dateFrom']
	dateto = params['dateTo']

	newwidget = widget.widget
	newwidget['data']['range']['from'] = datefrom
	newwidget['data']['range']['to'] = dateto

	updatedwidget = set_widget(newwidget, request.user)

	widget.widget = updatedwidget
	widget.save()

	if updatedwidget is None:
		#return 500
		responsedata = {
			'success': False,
			'message': 'Internal server error.'
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	return HttpResponse(json.dumps({'widget': updatedwidget}))

@login_required
def get_settings(request):
	settings = user_settings(request.user)
	return HttpResponse(json.dumps(settings))

@login_required
def alert_action(request):
	#return http bad request
	if not request.is_ajax():
		return HttpResponse('None ajax request')

	if request.method == 'POST':
		post_data = json.loads(request.body)
		post_data.update({'user': request.user})
		print 'so far good'
		# GET, ADD_NEW, MODIFY, REMOVE, MARK_NEW, MARK_NO_NEW, MARK_READ
		# print post_data['action']
		if post_data['action'] == 'ADD_NEW':
			try:
				alert = Alert(post_data)
				uid = alert.save()
			except IntegrityError as e:
				print e
				return HttpResponse(json.dumps({'success': False, 'message': 'Failed to save alert. Similar alert exists.'}))
			return HttpResponse(json.dumps({'success': True, 'message': 'Alert saved successfully.', 'uid': uid}))
		elif post_data['action'] == 'MODIFY':
			try:
				alert = Alert(post_data)
				alert.update()

			except NameError as e:
				print e
				return HttpResponse(json.dumps({'success': False, 'message': 'failed to modify alert'}))
			return HttpResponse(json.dumps({'success': True, 'message': 'Alert modified successfully.'}))
		elif post_data['action'] == 'DELETE':
			try:
				alerts = Alerts.objects.filter(user=request.user, uid=post_data['uid'])
				alerts.delete()
			except:
				print sys.exc_info()[0]
				return HttpResponse(json.dumps({'success': False, 'message': 'Delete failed.'}))
			return HttpResponse(json.dumps({'success': True, 'message': 'Alert deleted successfully.'}))
		elif post_data['action'] == 'MARK_READ':
			try:
				event = AlertEvents.objects.filter(user=request.user, event_id=post_data['uid'])
				event.update(read=True)
				return HttpResponse(json.dumps({'success': True, 'message': 'MARK_READ successful.'}))
			except (KeyError, AlertEvents.DoesNotExist, Alerts.DoesNotExist) as e:
				print e
				return HttpResponse(json.dumps({'success': False, 'message': 'MARK_READ failed.'}))
		elif post_data['action'] == 'MARK_NEW':
			try:
				last_mark_off = Settings.objects.get(user=request.user).alert_mark_off
				new_events_count = 0
				if last_mark_off is not None:
					new_events_count = AlertEvents.objects.filter(user=request.user, t_notify__gt=last_mark_off, notify=True, snoozed=False).count()

			except Settings.DoesNotExist as e:
				print e
				new_events_count = 0
			unread_events_count = AlertEvents.objects.filter(user=request.user, read=False, notify=True, snoozed=False).count()
			new_events = AlertEvents.objects.filter(user=request.user, notify=True, snoozed=False).reverse()[0:post_data['count']]
			alerts = []
			for event in new_events:
				try:
					widget = Widgets.objects.get(user=request.user, widget_id=event.widget)
					widget_title = widget.widget['title']
				except Widgets.DoesNotExist as e:
					print e
					widget_title = event.widget

				alerts.extend([{
					'uid': event.event_id, 
					'name': event.alert.name,
					'description': event.alert.description,
					'message': event.alert.message,
					'read': event.read, 
					't_notify': date_to_string(event.t_notify),
					'value': event.value, 
					'widget': widget_title,
					'station': event.station,
					'sensor': event.sensor,
					'calc': event.calc,
					'type': event.alert.type
					}])
			response_data = {
				'alerts': alerts,
				'new_count': new_events_count, 
				'unread': unread_events_count, 
				'success': True, 
				'message': 'MARK_NEW successful.'
			}
			return HttpResponse(json.dumps(response_data))

		elif post_data['action'] == 'MARK_OFF_NEW':
			
			try:
				event = AlertEvents.objects.filter(user=request.user, notify=True).last()
			except AlertEvents.DoesNotExist as e:
				print e
				return HttpResponse(json.dumps({'success': False, 'message': 'MARK_OFF_NEW Failed.'}))

			user_settings = Settings.objects.filter(user=request.user)
			user_settings.update(alert_mark_off=event.t_notify)

			return HttpResponse(json.dumps({'success': True}))

		elif post_data['action'] == 'GET_EVENT':
			try:
				event = AlertEvents.objects.get(user=request.user, event_id=post_data['uid'])
			except AlertEvents.DoesNotExist as e:
				print e
				return HttpResponse(json.dumps({'success': False, 'message': 'Alert event could not be reteived.'}))

			try:
				widget = Widgets.objects.get(user=request.user, widget_id=event.widget)
				widget_title = widget.widget['title']
			except Widgets.DoesNotExist as e:
				print e
				widget_title = event.widget

			alert_event = {
				'uid': event.event_id, 
				'name': event.alert.name,
				'description': event.alert.description,
				'message': event.alert.message,
				'read': event.read, 
				't_notify': date_to_string(event.t_notify),
				'value': event.value, 
				'widget': widget_title,
				'station': event.station,
				'sensor': event.sensor,
				'calc': event.calc,
				'success': True,
				'error': 'GET_EVENT successful.'
			}
			return HttpResponse(json.dumps(alert_event));
			

	elif request.method == 'GET':
		post_data = json.loads(request.GET.get('params'))
		if post_data['action'] == 'GET':
			try: 
				alert = Alerts.objects.get(uid=post_data['uid'], user=request.user)
			except (KeyError, Alerts.DoesNotExist) as e:
				print e
				return HttpResponse(json.dumps({'success': False, 'message': 'Error retreiving alert.'}))
			response_data = {
				'uid': alert.uid, 
				'name': alert.name,
				'description': alert.description,
				'sensors': alert.sensors,
				'extract': alert.extract,
				'logic': alert.logic, 
				'threshold': alert.threshold,
				'message': alert.message,
				't_beyond': alert.t_beyond,
				'calc': alert.calc, 
				'type': alert.type,
				'snooze': alert.snooze,
				'snooze_time': alert.snooze_time,
				'email_alert': alert.email_alert, 
				'sms_alert': alert.sms_alert, 
				'success': True,
				'error': ''
			}
			return HttpResponse(json.dumps(response_data))

@login_required
def settings_index(request):
	fc_stations = Stations.objects.filter(user=request.user, database='fc')
	dg_stations = Stations.objects.filter(user=request.user, database='dg')
	alerts = Alerts.objects.filter(user=request.user)
	dashboards = Dashboard.objects.filter(user=request.user)
	# t1 = datetime.datetime.now()
	# data_sensors = {}
	# for station in fc_stations:
	# 	data = StationData.objects.filter(station_id=station.station)
	# 	if data.exists():
	# 		data_sensors.update({station.station:[k for k, v in data.last().data.iteritems() if v != None]})
	# print (datetime.datetime.now() - t1).seconds
	
	return render(request, 'settings.html', {
			'name': request.user.first_name,
			'fc_stations': fc_stations,
			'dg_stations': dg_stations, 
			'alerts': alerts,
			'dashboards': dashboards
			# 'data_sensors':data_sensors			
			})

@login_required
def add_station(request):	
	
	if request.is_ajax():
		if request.method == 'POST':
			post_data = json.loads(request.body)
			if post_data['db'] == 'fc':
				response = add_fc_station(request.user, post_data)
			elif post_data['db'] == 'dg':
				response = add_dg_station(request.user, post_data)
	return HttpResponse(json.dumps(response))

@require_POST
def upload(request):
	file = upload_receive(request)
	instance = Files(user=request.user, file=file)
	instance.save()

	basename = os.path.basename(instance.file.path)

	file_dict = {
		'name' : basename,
        'size' : file.size,

        'url': settings.MEDIA_URL + basename,
        'thumbnailUrl': settings.MEDIA_URL + basename,

        'deleteUrl': reverse('jfu_delete', kwargs = { 'pk': instance.pk }),
        'deleteType': 'POST',
	}

	return UploadResponse(request, file_dict)

@require_POST
def upload_delete(request, pk):
    success = True
    try:
        instance = Files.objects.get(pk = pk)
        os.unlink(instance.file.path)
        instance.delete()
    except Files.DoesNotExist:
        success = False
    return JFUResponse(request, success)	


def load_files(request):
	return HttpResponse(json.dumps(list_files(request.user)))


def file_upload(request):
	if request.is_ajax():	
		if request.method == 'POST':
			form = FileUploadForm(files=request.FILES)
			instance = Files(user=request.user, file=request.FILES['file'])
			instance.save()
			return HttpResponse(json.dumps(list_files(request.user)))
	else:
		return HttpResponse(json.dumps(list_files(request.user)))


def delete_files(request):
	if request.is_ajax():
		if request.method == 'POST':
			file_lst = json.loads(request.body)
			for file in file_lst:
				db_file = Files.objects.filter(file=file)
				if db_file.exists():
					db_file.delete()
				db_file_unzipped = Files.objects.filter(file=file+'.kml')
				if db_file_unzipped.exists():
					db_file_unzipped.delete()
			return HttpResponse(json.dumps({'deleted':file_lst, 'success': True}))
	return HttpResponse(json.dumps({'deleted':[], 'success': False}))


def download_file(request):
	file = request.POST['name']
	db_file = Files.objects.filter(user=request.user, file=file)
	if db_file.exists():
		filename = db_file[0].file.name.split('/')[-1]
		response = HttpResponse(db_file[0].file, content_type='application/.docx')
		response['Content-Disposition'] = 'attachment; filename=%s' % filename
		return response


def get_url(request):
	if request.method == 'POST':
		file = json.loads(request.body)
		db_file = Files.objects.filter(user=request.user, file=file[0])
		if db_file.exists():
			basename = os.path.basename(db_file[0].file.path)
			url = settings.MEDIA_URL + basename
			if db_file[0].file.name.split('.')[-1] == 'kmz':
				url = get_unzip(db_file[0].file.name, request.user)
			return HttpResponse(json.dumps({'url': url}))

@login_required
def remove_widget(request):
	if request.is_ajax():
		if request.method == 'POST':
			post_data = json.loads(request.body)
			widget = Widgets.objects.filter(widget_id=post_data['id'], user=request.user)
			if widget.exists():
				widget.delete()
				return HttpResponse(json.dumps({'success':True}))
	return HttpResponse(json.dumps({'success':False}))

@login_required
def change_alias(request):
	if request.is_ajax:
		if request.method == 'POST':
			post_data = json.loads(request.body)
			if post_data.has_key('station_id'):
				station = Stations.objects.filter(station=post_data['station_id'])
				if station.exists():
					station.update(name=post_data['alias'])
					post_data['success'] = True
					post_data['message'] = 'Alias successfully changed. Please refresh page.'
				else:
					post_data['success'] = False
					post_data['message'] = 'Station does not exist. Please check parameter and try again.'
			elif post_data.has_key('sensor_id'):
				station = Stations.objects.filter(station=post_data['sensor_id'].split('-')[1])
				if station.exists():
					sensors = station[0].sensors
					if sensors.has_key(post_data['sensor_id'].split('-')[2]):
						sensors[post_data['sensor_id'].split('-')[2]] = post_data['alias']
						station.update(sensors=sensors)
						post_data['success'] = True
						post_data['message'] = ' Alias successfully changed. Please refresh page.'
					elif len(post_data['sensor_id'].split('-')) > 2:
						if sensors.has_key(post_data['sensor_id'].split('-')[2]+'-'+post_data['sensor_id'].split('-')[3]):
							sensors[post_data['sensor_id'].split('-')[2]+'-'+post_data['sensor_id'].split('-')[3]] = post_data['alias']
							station.update(sensors=sensors)
							post_data['success'] = True
							post_data['message'] = ' Alias successfully changed. Please refresh page.'
					else:
						post_data['success'] = False
						post_data['message'] = 'Sensor does not exist. Please check parameters and try again.'
				else:
					post_data['success'] = False
					post_data['message'] = 'Station does not exist. Please check parameter and try again.'
			else:
				post_data['success'] = False
				post_data['message'] = 'Station does not exist. Please check parameter and try again.'
		else:
			post_data['success'] = False
			post_data['message'] = 'Invalid request. Please check parameter and try again.'
	else:
		post_data['success'] = False
		post_data['message'] = 'Invalid request. Please check parameter and try again.'
	return HttpResponse(json.dumps(post_data))

@login_required
def remove_station(request):
	if request.is_ajax:
		if request.method == 'POST':
			params = json.loads(request.body)
			try:
				station = Stations.objects.get(user=request.user, station=params['station_id'])
				station.delete()
				res = {'message':'Station deleted.', 'success':True, 'station_id':params['station_id']}
				return HttpResponse(json.dumps(res))
			except Stations.DoesNotExist:
				return HttpResponse(json.dumps({'message':'Station does not exist.', 'success':False, 'station_id':params['station_id']}))
		else:
			pass
	else:
		pass

@login_required
def change_setting(request):
	if request.is_ajax:
		if request.method == 'POST':
			params = json.loads(request.body)
			defaults = {
				'calc_color':{},
				'sensor_color':{},
				'calc_graph':{},
				'sensor_graph':{},
				'cportions':{},
				'chours':{},
				'ddays':{},
				'arain':{}
			}
			if params['opt'] == 'graph_color':
				if params['type'] == 'calc':
					defaults.update({'calc_color':{params['attr']:params['value']}})
				elif params['type'] == 'sensor':
					defaults.update({'sensor_color':{params['attr']:params['value']}})
			elif params['opt'] == 'graph_type':
				if params['type'] == 'calc':
					defaults.update({'calc_graph':{params['attr']:params['value']}})
				elif params['type'] == 'sensor':
					defaults.update({'sensor_graph':{params['attr']:params['value']}})
			elif params['opt'] == 'cp_reset_date':
				defaults.update({'cportions':{params['attr']:params['value']}})
			elif params['opt'] == 'ch_reset_date' or 'ch_threshold':
				defaults.update({'chours':{params['attr']:params['value']}})
			elif params['opt'] == 'dd_reset_dt' or 'dd_threshold':
				defaults.update({'ddays':{params['attr']:params['value']}})
			elif params['opt'] == 'ar_reset_dt':
				defaults.update({'arain':{params['attr']:params['value']}})
			settings, exists = Settings.objects.get_or_create(user=request.user, defaults=defaults)
			if not exists:
				if params['opt'] == 'graph_color':
					if params['type'] == 'calc':
						new = settings.calc_color
						new.update({params['attr']:params['value']})
						settings.calc_color == new
						settings.save()
					elif params['type'] == 'sensor':
						new = settings.sensor_color
						new.update({params['attr']:params['value']})
						settings.sensor_color = new
						settings.save()
				elif params['opt'] == 'graph_type':
					if params['type'] == 'calc':
						new = settings.calc_graph
						new.update({params['attr']:params['value']})
						settings.calc_graph = new
						settings.save()
					elif params['type'] == 'sensor':
						new = settings.sensor_graph
						new.update({params['attr']:params['value']})
						settings.sensor_graph = new
						settings.save()
				elif params['opt'] == 'cp_reset_dt':
					new = settings.cportions
					new.update({params['attr']:params['value']})
					settings.cportions = new
					settings.save()
				elif params['opt'] == 'ch_reset_dt' or params['opt'] == 'ch_threshold':
					new = settings.chours
					new.update({params['attr']:params['value']})
					settings.chours = new
					settings.save()
				elif params['opt'] == 'dd_reset_dt' or params['opt'] == 'dd_threshold':
					new = settings.ddays
					new.update({params['attr']:params['value']})
					settings.ddays = new
					settings.save()
				elif params['opt'] == 'ar_reset_dt':
					new = settings.arain
					new.update({params['attr']:params['value']})
					settings.arain = new
					settings.save()
			return HttpResponse(json.dumps({'message':'Operation succeeded.', 'success':True}))
	return HttpResponse(json.dumps({'message':'Operation failed.', 'success':False}))

@login_required
def adddashboard(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Non-ajax requests not allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	try:
		dashboard = Dashboard(user=request.user, name=params['name'])
		dashboard.save()
	except (KeyError, ValueError) as e:
		print e
		responsedata = {
			'success': False,
			'message': 'Internal server error.'
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = {
		'success': True,
		'message': 'Dashboard created.',
		'uid': str(dashboard.uid)
	}

	return HttpResponse(json.dumps(responsedata))

@login_required
def removedashboard(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Non-ajax requests not allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	try:
		dashboard = Dashboard.objects.filter(user=request.user, uid=params['uid'])
	except KeyError as e:
		print e
		responsedata = {
			'success': False,
			'message': 'Internal server error.'
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	if dashboard.exists():
		dashwidgets = Widgets.objects.filter(user=request.user, dashboard=dashboard)
		# cannot delete if dashboard contains widgets
		if dashwidgets.exists():
			responsedata = {
				'success': False,
				'message': 'Dashboard contains widgets. Operation failed.'
			}
			return HttpResponse(json.dumps(responsedata), status=403)
		# at least 1 dashboard must exist
		if Dashboard.objects.filter(user=request.user).count() < 2:
			responsedata = {
				'success': False,
				'message': 'At least 1 dashboard must exist. Operation failed.'
			}
			return HttpResponse(json.dumps(responsedata), status=403)			

		try:
			dashboard.delete()
		except:
			responsedata = {
				'success': False,
				'message': 'Internal server error. Operation failed.'
			}
			return HttpResponse(json.dumps(responsedata), status=500)
	else:
		responsedata = {
			'success': False,
			'message': 'Dashboard not found. Operation failed.'
		}
		return HttpResponse(json.dumps(responsedata), status=404)

	responsedata = {
		'success': True,
		'message': 'Dashboard deleted.'
	}

	return HttpResponse(json.dumps(responsedata))

@login_required
def editdashboard(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Non-ajax requests not allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	try:
		dashboard = Dashboard.objects.get(user=request.user, uid=params['uid'])
	except (KeyError, Dashboard.DoesNotExist) as e:
		print e
		responsedata = {
			'success': False,
			'message': 'Internal server error.'
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	try:
		dashboard.name = params['name']
		dashboard.save()
	except:
		responsedata = {
			'success': False,
			'message': 'Internal server error. Operation failed.'
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = {
		'success': True,
		'message': 'Dashboard changed.'
	}

	return HttpResponse(json.dumps(responsedata))


@login_required
def snooze_state_change(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	try:
		alert = Alerts.objects.filter(user=request.user, uid=params['alert_id']).update(snooze=params['state'])
	except (Alerts.DoesNotExist, KeyError) as e:
		responsedata = {
			'success': False,
			'message': e
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = {
		'success': True,
		'message': 'Request succeeded.'
	}
	return HttpResponse(json.dumps(responsedata), status=200)


@login_required
def add_stat_widget(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	#get user's current dashboard
	try:
		active_dashboard = Dashboard.objects.get(user=request.user, active=True)

	except Dashboard.DoesNotExist as e:
		responsedata = {
			'id': None, 
			'success': False,
			'message': 'Please add widget inside a dashboard.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	#get new widget id
	widget_id = uuid.uuid4().hex

	#widget attributes
	widget_attr = {'title':params['name'], 'color':params['color']}

	#create new stat widget
	try:
		widget = Widgets(user=request.user, index=int(params['index']), widget_id=widget_id, widget_type='stat',\
		widget=widget_attr, dashboard=active_dashboard)
		widget.save()
	except (KeyError, ValueError, IntegrityError) as e:
		responsedata = {
			'id': None, 
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = {
		'id': widget.widget_id, 
		'success': True,
		'message': 'Widget created.'
	}
	return HttpResponse(json.dumps(responsedata), status=200)

@login_required
def delete_stat_widget(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	#get the widget to delete
	try:
		widget = Widgets.objects.get(widget_id=params['widget'])
	except (KeyError, Widgets.DoesNotExist) as e:
		responsedata = {
			'id': params['widget'], 
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	#if widget has data do not delete
	data = widget.dataset.all()
	if data.exists():
		responsedata = {
			'id': params['widget'],
			'success': False,
			'message': 'Cannot delete widget with data.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)
	else:
		#if widget has no data proceed with delete
		try:
			widget.delete()
			del widget
		except Exception as e:
			responsedata = {
				'id': params['widget'], 
				'success': False,
				'message': e.message
			}
			return HttpResponse(json.dumps(responsedata), status=500)
		#return success response
		responsedata = {
			'id': params['widget'], 
			'success': True,
			'message': 'Widget deleted.'
		}
		return HttpResponse(json.dumps(responsedata), status=200)

@login_required
def fetch_stat_widget(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	#get the widget to fetch
	try:
		widget = Widgets.objects.get(widget_id=params['widget'], user=request.user)
	except (KeyError, Widgets.DoesNotExist) as e:
		responsedata = {
			'id': params['widget'], 
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	#fetch widget
	responsedata = {
		'id': widget.widget_id,
		'success': True,
		'message': 'Widget fetched.',
		'index': widget.index, 
		'color': widget.widget['color'], 
		'name': widget.widget['title']
	}
	return HttpResponse(json.dumps(responsedata), status=200)


@login_required
def change_stat_widget(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	#get the widget to change
	try:
		widget = Widgets.objects.get(widget_id=params['widget'], user=request.user)
		widget.widget = {'color': params['color'], 'title':params['name']}
		widget.index = params['index']
		widget.save()
	except (KeyError, Widgets.DoesNotExist) as e:
		responsedata = {
			'id': params['widget'], 
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	#return success
	#fetch widget
	responsedata = {
		'id': widget.widget_id,
		'success': True,
		'message': 'Widget changed.',
		'index': widget.index, 
		'color': widget.widget['color'], 
		'name': widget.widget['title']
	}
	return HttpResponse(json.dumps(responsedata), status=200)


@login_required
def add_stat_data(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)
	
	#get related widget
	try:
		widget = Widgets.objects.get(user=request.user, widget_id=params['widget'])
	except Widgets.DoesNotExist as e:
		responsedata = {
			'success': False,
			'message': 'Corresponding widget not found.'
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	#get related chart widget
	try:
		chart_widget = Widgets.objects.get(user=request.user, widget_id=params['chart'])
	except (Widgets.DoesNotExist, KeyError) as e:
		chart_widget = None

	try:
		sensor = params['sensor']
	except KeyError as e:
		sensor = None
	#create widget data
	try:
		data = Data(user=request.user, name=params['name'], widget=widget, function=params['data'], sensor=sensor, extract=params['extract'],\
			chart=chart_widget, date_from=params['from'], date_to=params['to'], unit='', stale=False)
		data.save()
	except Exception as e:
		responsedata = {
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = set_stat_widget(data.id)
	responsedata.update({'id':data.id})

	return HttpResponse(json.dumps(responsedata), status=200)



@login_required
def change_stat_data(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	#get related chart widget
	try:
		chart_widget = Widgets.objects.get(user=request.user, widget_id=params['chart'])
	except (Widgets.DoesNotExist, KeyError) as e:
		chart_widget = None

	#if sensor not provided
	try:
		sensor = params['sensor']
	except KeyError as e:
		sensor = None

	#get related widget data to update
	try:
		data = Data.objects.get(user=request.user, id=params['data_id'])
		data.name = params['name']
		data.function = params['data']
		data.extract = params['extract']
		data.chart = chart_widget
		data.date_from = params['from']
		data.date_to = params['to']
		data.unit = ''
		data.sensor = sensor
		data.save()
		# data.update(name=params['name'], function=params['data'], sensor=params['sensor'], extract=params['extract'],\
		# chart=chart_widget, date_from=params['from'], date_to=params['to'], unit='')
	except Exception as e:
		responsedata = {
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = set_stat_widget(data.id)
	#add name and Id to the response
	responsedata.update({
		'id':data.id,
		'name': data.name
		})

	return HttpResponse(json.dumps(responsedata), status=200)

@login_required
def fetch_stat_data(request):

	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	try:
		widget_data = Data.objects.get(user=request.user, id=params['data_id'])
	except Exception as e:
		responsedata = {
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = {
		'success': True,
		'message': '',
		'name': widget_data.name, 
		'data': widget_data.function, 
		'sensor': widget_data.sensor, 
		'extract': widget_data.extract, 
		'chart': widget_data.chart.widget_id if widget_data.chart is not None else None,
		'from': date_to_string(widget_data.date_from) if widget_data.date_from is not None else None,
		'to': date_to_string(widget_data.date_to) if widget_data.date_to is not None else None,
	}

	return HttpResponse(json.dumps(responsedata), status=200)


@login_required
def delete_stat_data(request):
	
	if not request.is_ajax() or request.method != 'POST':
		#return method not allowed
		responsedata = {
			'success': False,
			'message': 'Only ajax with POST is allowed.'
		}
		return HttpResponse(json.dumps(responsedata), status=405)

	params = json.loads(request.body)

	try:
		widget_data = Data.objects.get(user=request.user, id=params['data_id'])
		widget_data.delete()
	except Exception as e:
		responsedata = {
			'success': False,
			'message': e.message
		}
		return HttpResponse(json.dumps(responsedata), status=500)

	responsedata = {
		'success': True,
		'message': 'Data deleted.'
	}
	return HttpResponse(json.dumps(responsedata), status=200)


def resize_chart(request):
	""" Resize chart widget panel
	"""
	try:
		params = json.loads(request.body)
		widget = Widgets.objects.get(user=request.user, widget_id=params['widget_id'])
		expand = params['expand']
		widget.expand = expand
		widget.save()
		return HttpResponse(json.dumps({'expand': widget.expand}))
	except Exception, e:
		raise e
