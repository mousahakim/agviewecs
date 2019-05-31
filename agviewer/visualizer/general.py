
# notif_dict = {
	# 'name': '',
	# 'description': '',
	# 'logic': '',
	# 'threshold': '',
	# 'sensor': '',
	# 'message_es': '',
	# 'message_en': '',
	# 'read': '',
	# 'sent': ''
# }
from django.contrib.auth.models import User
from django.db.models import Q
from visualizer.models import Alerts, AlertEvents, AppUser, Stations, Widgets, SMTPConfig
from visualizer.tasks import async_alert
from visualizer.utils import date_to_string, parse_date
import datetime, uuid, sys, smtplib
from datetime import timedelta
from django.db import IntegrityError

class Alert:
	"""docstring for Alert"""
	def __init__(self, alert_dict):
		self.alert_dict = alert_dict

	#class functions
	@classmethod
	def has_alerts(cls, user, sensor, calc):
		"""check if widget has any
		alerts setup return list of alert object(s)"""
		if sensor is not None and calc is not None:
			alerts = Alerts.objects.filter(Q(sensors__contains=sensor) | Q(calc__contains=calc)).filter(user=user)
			return alerts
		elif sensor is not None:
			alerts = Alerts.objects.filter(sensors__contains=sensor, user=user)
			return alerts
		elif calc is not None:
			alerts = Alerts.objects.filter(calc__contains=calc, user=user)
			return alerts
		else:
			return []

	@classmethod
	def alert_from_model_obj(cls, model_obj):
		alert_dict = {
			'user': model_obj.user,
			'uid': model_obj.uid, 
			'name': model_obj.name,
			'description': model_obj.description,
			'sensors': model_obj.sensors,
			'extract': model_obj.extract,
			'logic': model_obj.logic, 
			'threshold': model_obj.threshold,
			'message': model_obj.message,
			't_beyond': model_obj.t_beyond,
			'snooze': model_obj.snooze, 
			'snooze_time':model_obj.snooze_time,
			'calc': model_obj.calc, 
			'type': model_obj.type, 
			'email_alert': model_obj.email_alert, 
			'sms_alert': model_obj.sms_alert
		}

		alert = Alert(alert_dict)
		return alert

	@classmethod
	def get_unsent(user):
		"""get a list of user's unsent 
		alerts"""
		alerts = Alerts.object.filter(user=user, sent=False)
		return alerts

	@classmethod
	def get_unread(user):
		"""get a list of user's unread 
		alerts"""
		alerts = Alerts.object.filter(user=user, sent=False)
		return alerts

	@classmethod
	def has_email(self, user):
		"""check user details for
		missing important info like
		email and phone no."""
		try:
			appuser = AppUser.objects.get(user=user)
		except AppUser.DoesNotExist:
			return

		if appuser.email_add is None or appuser.email_add == '':
			return False
		return True

	@classmethod
	def get_email(self, user):
		"""
		get user's email 
		"""
		try: 
			appuser = AppUser.objects.get(user=user)
		except AppUser.DoesNotExist as e:
			print e
			return

		return appuser.email_add

	@classmethod
	def has_phone_no(self, user):
		"""check user details for
		missing important info like
		email and phone no."""
		try:
			appuser = AppUser.objects.get(user=user)
		except AppUser.DoesNotExist:
			return

		if appuser.phone is None or appuser.phone == '':
			return False
		return True 

	@classmethod
	def get_phone(self, user):
		"""
		get user's email 
		"""
		try: 
			appuser = AppUser.objects.get(user=user)
		except AppUser.DoesNotExist as e:
			print e
			return
			
		return appuser.phone_number

	@classmethod
	def create_config_alert(self, user, msg):
		"""If important user details are
		missing send warning"""
		time = datetime.datetime.now()
		note = self({
			'title': 'System alert',
			'alert': None,
			'message': msg,
			'read': False,
			'sent': False, 
			'time': time, 
			'event_id': date_to_string(time)+title,
			'count': 0
		})

		note.send_alert(user)

		
	#methods
	def update(self): 
		"""update alert object"""
		alert = self.alert_dict
		extract = alert['extract']
		try:
			snooze_time = alert['snooze_time']
		except ValueError:
			snooze_time = 0

		if extract == '':
			extract = None
		try:
			alert_obj = Alerts.objects.filter(user=alert['user'], uid=alert['uid']).update(name=alert['name'], description=alert['description'],\
				sensors=alert['sensors'], extract=extract, logic=alert['logic'], threshold=int(alert['threshold']), message=alert['message'], calc=alert['calc'],\
				type=alert['type'], email_alert=alert['email_alert'], sms_alert=alert['sms_alert'], t_beyond=alert['t_beyond'], snooze=alert['snooze'],\
				snooze_time=snooze_time)
		except:
			print sys.exc_info()[0]
			print 'error in update'

	def save(self):
		"""save alert object to db"""

		alert = self.alert_dict
		uid = str(uuid.uuid4())
		extract = alert['extract']
		try:
			snooze_time = alert['snooze_time']
		except ValueError:
			snooze_time = 0

		if extract == '':
			extract = None
		try:
			alert_obj = Alerts(
				uid=uid, user=alert['user'], name=alert['name'], description=alert['description'], sensors=alert['sensors'], \
				extract=extract, logic=alert['logic'], threshold=int(alert['threshold']), message=alert['message'], calc=alert['calc'],\
				type=alert['type'], email_alert=alert['email_alert'], snooze=alert['snooze'], snooze_time=snooze_time, sms_alert=alert['sms_alert'],\
				t_beyond=alert['t_beyond'])
			alert_obj.save()

		except KeyError as e:
			print e
			return
		return uid

	def save_event(self, event):
		"""save alert event to db"""

		alert = self.alert_dict
		try:
			alerts_obj = Alerts.objects.get(user=alert['user'], uid=alert['uid'])
		except Alerts.DoesNotExist as e:
			print e 
			return
		uid = str(uuid.uuid4())
		event_id = uid+'.'+date_to_string(parse_date(event['date']))
		calc = event['calc'] if event['calc'] is not None else ''
		sensor = ''
		station_name = ''
		if event['sensor'] is not None:
			try:
				station = Stations.objects.get(user=alert['user'], station=event['sensor'][0].split('-')[1])
				station_name = station.name
				for item in event['sensor']:
					if item.split('-')[0] ==  'dg':
						sensor += station.sensors[item.split('-')[-2]+'-'+item.split('-')[-1]] + '&#13;&#10;'
					else:
						sensor += station.sensors[item.split('-')[-1]] + '&#13;&#10;' 
			except (KeyError, Stations.DoesNotExist) as e:
				print e
		
		# widget = ''
		# try:
		# 	widget = Widgets.objects.get(widget_id=event['widget_id'], user=alert['user']).widget['title']
		# except (KeyError, Widgets.DoesNotExist) as e:
		# 	print e

		try:
			alert_event_obj = AlertEvents(
				user=alert['user'], alert=alerts_obj, read=False, sent=False, time=event['date'], value=float(event['value']),\
				 event_id=event_id, widget=event['widget_id'], station=station_name, sensor=sensor, calc=calc, sensor_id=event['sensor'][0],\
				 notify=False, t_notify=datetime.datetime.now(), snoozed=event['snoozed'])
			alert_event_obj.save()
			return event_id
		except (KeyError, IntegrityError) as e:
			print e


	def watch(self, event, sensor=None, calc=None):
		"""watch for alert
		 occurrences.
		 event is dict with keys: 'widget_id', 'date', 'value' 
		"""

		alert = self.alert_dict
		# print 'in watch'
		#get the last event for this alert
		try:
			alerts_obj = Alerts.objects.get(uid=alert['uid'])
			related_events = AlertEvents.objects.filter(alert=alerts_obj, widget=event['widget_id'], notify=False)
			related_notified_events = AlertEvents.objects.filter(alert=alerts_obj, widget=event['widget_id'], notify=True)
			if sensor is not None:
				related_events = AlertEvents.objects.filter(alert=alerts_obj, widget=event['widget_id'], sensor_id=sensor, notify=False)
				related_notified_events = AlertEvents.objects.filter(alert=alerts_obj, widget=event['widget_id'], sensor_id=sensor, notify=True)
			last_event = related_events.last()
			last_notified_event = related_notified_events.last()
		except Alerts.DoesNotExist as e:
			print e
			return

		last_not_snoozed_event = related_notified_events.filter(snoozed=False).last()
		#if not snoozed mark alertevent.snoozed = False
		snoozed = False
		#if snooze is switched on
		if alert['snooze']:
			#evaluate only if there is an existing none snoozed event
			if last_not_snoozed_event is not None:
				#if time greater than self.snooze_time has passed mark event.snoozed = False
				if parse_date(event['date']) - last_not_snoozed_event.t_notify < timedelta(hours=alert['snooze_time']):
					snoozed = True

		#update event params
		event.update({'calc': calc, 'snoozed':snoozed})

		if calc is not None and calc == alert['calc'] or sensor is not None and sensor in alert['sensors']:
			# print 'nothing is right'
			#prevent re-evaluation of data
			if last_notified_event is not None:
				if parse_date(event['date']) <= last_notified_event.t_notify:
					return
			if alert['logic'] == 'lt':
				# print event['value'], alert['threshold']
				#if value is beyond threshold
				if float(event['value']) < float(alert['threshold']):
			 		#if t_beyond is zero notify immediately
			 		print float(event['value']), float(alert['threshold'])
			 		if alerts_obj.t_beyond == 0:
			 			print 't_beyond is 0'
			 			if last_event is None:
			 				print 'creating new event'
			 				event_id = self.save_event(event)
			 				try:
			 					alert_event = AlertEvents.objects.get(event_id=event_id)
			 					alert_event.t_notify = parse_date(event['date'])
			 					alert_event.notify = True
			 					alert_event.snoozed = snoozed
			 					alert_event.save()
			 					print 'creating new event success'
			 					print alert_event.t_notify
			 					# async_alert(event_id)
			 				except AlertEvents.DoesNotExist as e:
			 					print 'alert event already exists.'
			 					print e
			 					return
			 				except IntegrityError as e:
			 					print e
			 					return
			 			else:
			 				try:
			 					print 'editing old event'
				 				last_event.t_notify = parse_date(event['date'])
				 				last_event.notify = True
				 				last_event.snoozed = snoozed
				 				last_event.save()
				 				#do not send email/sms notification if snoozed
			 					if snoozed:
			 						return
				 				async_alert(last_event.event_id)
				 				print 'editing old event success'
				 			except IntegrityError as e:
				 				print 'alert event already exists.'
			 					print e
			 					return
			 		#if value has been beyond threshold for a while
			 		if last_event is not None:
			 			#if value has been boyond threshold long enough to alert
			 			if parse_date(event['date']) - last_event.time >= timedelta(hours=alerts_obj.t_beyond):
			 				try:
				 				last_event.t_notify = parse_date(event['date'])
				 				last_event.notify = True
				 				last_event.snoozed = snoozed
				 				last_event.save()
				 				#do not send email/sms notification if snoozed
			 					if snoozed:
			 						return
				 				async_alert(last_event.event_id)
				 			except IntegrityError as e:
				 				print 'alert event already exists.'
			 					print e
			 					return
			 		#first time value goes beyond threshold
			 		else:
			 			self.save_event(event)
			 	#value comes within threshold before t_beyond time has passed
			 	#so event is deleted wihtout notifying user
			 	else:
			 		related_events.delete()
			 		
			elif alert['logic'] == 'gt':
				if float(event['value']) > float(alert['threshold']):
			 		if alerts_obj.t_beyond == 0:
			 			if last_event is None:
			 				event_id = self.save_event(event)
			 				try:
			 					alert_event = AlertEvents.objects.get(event_id=event_id)
			 					alert_event.t_notify = parse_date(event['date'])
			 					alert_event.notify = False
			 					alert_event.snoozed = snoozed
			 					alert_event.save()
			 					# async_alert(event_id)
			 				except (IntegrityError, AlertEvents.DoesNotExist) as e:
			 					print 'alert event already exists.'
			 					print e
			 					return
			 			else:
			 				try:
				 				last_event.t_notify = parse_date(event['date'])
				 				last_event.notify = True
				 				last_event.snoozed = snoozed
				 				last_event.save()
				 				#do not send email/sms notification if snoozed
			 					if snoozed:
			 						return
				 				async_alert(last_event.event_id)
				 			except IntegrityError as e:
				 				print 'alert event already exists.'
			 					print e
			 					return
			 		if last_event is not None:
			 			if parse_date(event['date']) - last_event.time >= timedelta(hours=alerts_obj.t_beyond):
			 				try:
				 				last_event.t_notify = parse_date(event['date'])
				 				last_event.notify = True
				 				last_event.snoozed = snoozed
				 				last_event.save()
				 				#do not send email/sms notification if snoozed
			 					if snoozed:
			 						return
				 				async_alert(last_event.event_id)
				 			except IntegrityError as e:
				 				print 'alert event already exists.'
			 					print e
			 					return
			 		else:
			 			self.save_event(event)
			 	else:
			 		related_events.delete()
			elif alert['logic'] == 'et':
				if float(event['value']) == float(alert['threshold']):
					if alerts_obj.t_beyond == 0:
						if last_event is None:
							event_id = self.save_event(event)
							try:
			 					alert_event = AlertEvents.objects.get(event_id=event_id)
			 					alert_event.t_notify = parse_date(event['date'])
			 					alert_event.notify = False
			 					alert_event.snoozed = snoozed
			 					alert_event.save()
			 					# async_alert(event_id)
			 				except (IntegrityError, AlertEvents.DoesNotExist) as e:
			 					print 'alert event already exists.'
			 					print e
			 					return
			 			else:
			 				try:
				 				last_event.t_notify = parse_date(event['date'])
				 				last_event.notify = True
				 				last_event.snoozed = snoozed
				 				last_event.save()
				 				#do not send email/sms notification if snoozed
			 					if snoozed:
			 						return
				 				async_alert(last_event.event_id)
				 			except IntegrityError as e:
				 				print 'alert event already exists.'
			 					print e
			 					return
			 		if last_event is not None:
			 			if parse_date(event['date']) - last_event.time >= timedelta(hours=alerts_obj.t_beyond):
			 				try:
				 				last_event.t_notify = parse_date(event['date'])
				 				last_event.notify = True
				 				last_event.snoozed = snoozed
				 				last_event.save()
				 				#do not send email/sms notification if snoozed
			 					if snoozed:
			 						return
				 				async_alert(last_event.event_id)
				 			except IntegrityError as e:
				 				print 'alert event already exists.'
			 					print e
			 					return
			 		else:
			 			self.save_event(event)
			 	else:
			 		related_events.delete()


	def send_alert(self, user):
		"""send web alert """
		alert = self.alert_dict
		alert_event = AlertEvents(
			user=user, alert=alert['alert'], read=alert['read'], sent=alert['sent'], time=alert['time'], count=alert['count'], event_id=alert['event_id'])
		alert_event.save()

	def send_email(self, event_id):
		"""send alert through
			email """
		alert = self.alert_dict

		try:
			event = AlertEvents.objects.get(event_id=event_id)
		except AlertEvents.DoesNotExist as e:
			print e
			return

		try:
			configs = SMTPConfig.objects.get(user_this=True)
		except SMTPConfig.DoesNotExist as e:
			print e
			return

		try:
			widget = Widgets.objects.get(widget_id)
			widget_title = widget.widget['title']
		except Widgets.DoesNotExist as e:
			print e
			widget_title = 'Non-existing widget'

		user = event.user

		if not self.has_email(user):
			print 'no email address provided'
			return

		from_ = configs.username
		to = self.get_email(user).split(',')

		subject = 'AgViewer: ' + alert['name'] + ' '+ upper(alert['type'])
		body = widget_title + '\t\t' + event.t_notify + '\n' + alert['message']

		message = """From: %s\nTo: %s\nSubject: %s\n\n%s
		""" % (from_, ", ".join(to), subject, body)

		try:
			if configs.tls:
				server = smtplib.SMTP(configs.server_address, configs.port)
				if configs.esmtp:
					server.ehlo()
				else:
					server.helo()
				server.starttls()
				server.login(configs.username, configs.password)
				server.sendmail(from_, to, message)
				server.close()
				print 'email sent successfully.'
				try:
					email_noti = EmailNotification(user=user, subject=subject, content=body, success=True)
					email_noti.save()
				except:
					print 'failed to save email notification'
			elif configs.ssl:
				server = smtplib.SMTP_SSL(configs.server_address, configs.port)
				if configs.esmtp:
					server.ehlo()
				else:
					server.helo()
				server.login(configs.username, configs.password)
				server.sendmail(from_, to, message)
				server.close()
				print 'email sent successfully.'
				try:
					email_noti = EmailNotification(user=user, subject=subject, content=body, success=True)
					email_noti.save()
				except:
					print 'failed to save email notification'
		except:
			print 'failed to send email.'
			try:
				email_noti = EmailNotification(user=user, subject=subject, content=body, success=False, error='failed to send email')
				email_noti.save()
			except:
				print 'failed to save email notification'





		# save alert event to db

	def send_sms(self):
		"""send alert through
			sms """
		pass

	def is_type_sms(self):
		"""check if alert
		type is sms"""
		pass

	def is_type_email(self):
		"""check if alert
		type is email"""
		pass

	def mark_as_read(self):
		"""mark alert as read"""
		pass

	def is_duplicate(self):
		"""check if similar alert
		already exists"""
		pass




