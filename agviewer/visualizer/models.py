from django.db import models
from django.db.models import ForeignKey
import hashlib, uuid, time, os
from django.conf import settings
from django.dispatch import receiver
from jsonfield import JSONField
from django.core.validators import RegexValidator
from django.utils import timezone
#from django.contrib.auth.models import User
# Create your models here.
class Ambient(models.Model):

	name = models.CharField(max_length=100, primary_key=True)
	# min_temp = [{}]
	# max_temp = [{}]

	def __str__(self):
		return self.name

class subAmbient(Ambient):

	avg_temp = []

class UI_MicroChart(models.Model):

	name = models.CharField(max_length=25, primary_key=True)
	icon = models.CharField(max_length=100)
	#user = User()
	data = models.CharField(max_length=100) # number of charts
	chart_type = models.IntegerField() # 1 = line chart, 2 = bar chart
	line_color = models.CharField(max_length=7)	
	sequence = models.IntegerField()		

class UI_Chart(models.Model):

	name = models.CharField(max_length=25, primary_key=True)
	icon = models.CharField(max_length=100)
	#user = User()
	data = models.CharField(max_length=100) # number of charts
	chart_type = models.IntegerField() # 1 = line chart, 2 = bar chart
	line_color = models.CharField(max_length=7)
	sequence = models.IntegerField()
	size = models.IntegerField()


class AppUser(models.Model):

	user =  models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
	email_add = models.CharField(blank=True, max_length=300)
	phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
	phone_number = models.CharField(validators=[phone_regex], blank=True, max_length=16) # validators should be a list
	fc_username = models.CharField(max_length=100)
	fc_password = models.CharField(max_length=200)
	fc_salt = models.CharField(max_length=200)
	dg_username = models.CharField(max_length=100)
	dg_password = models.CharField(max_length=100)
	pub_key = models.CharField(max_length=100)
	prv_key = models.CharField(max_length=100)
	access_chart_settings = models.BooleanField(default=True)


class Station_Data(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	database = models.CharField(max_length=2)
	station_name = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True, primary_key=True)
	f_date = models.DateTimeField()
	data = JSONField()

	class Meta:
		ordering = ["f_date"]


class Widgets(models.Model):

	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	index = models.IntegerField()
	widget_id = models.CharField(max_length=100, primary_key=True)
	widget_type = models.CharField(max_length=100)
	widget = JSONField()
	dashboard = models.ForeignKey('Dashboard', null=True, default=None)
	expand = models.BooleanField(default=False)
	class Meta:
		ordering = ['index']

class StationList(models.Model):

	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	station_list = JSONField()

class SensorList(models.Model):

	station = models.CharField(max_length=100, primary_key=True)
	sensor_list = JSONField()

class SoilMS(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	sensor_list = JSONField(primary_key=True)

class DSensorList(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	sensor_id = models.CharField(max_length=100, primary_key=True)
	sensor_list = JSONField() # {station_id:'', station_name:'', sensor_id:'', sensor_name:''}

class DStationList(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	station_id = models.CharField(max_length=100)
	station_name = models.CharField(max_length=100)

class SensorCodes(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	sensor_id = models.CharField(max_length=50, primary_key=True)
	sensor_name = models.CharField(max_length=100)
	sensor_unit = models.CharField(max_length=100)
	axis_code = models.CharField(max_length=100)
	axis_name = models.CharField(max_length=100)

class Chip(models.Model):
	sensor_id = models.CharField(max_length=100) # station + sensor. for dg station+sensor+port
	date = models.DateTimeField(primary_key=True)
	value = JSONField()
	class Meta:
		ordering = ['date']


class Files(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	file = models.FileField()


class StationData(models.Model):
	created = models.DateTimeField(editable=False)
	modified = models.DateTimeField()
	station_id = models.CharField(max_length=100, db_index=True)
	database = models.CharField(max_length=3, db_index=True)
	date = models.DateTimeField(db_index=True)
	mrid = models.IntegerField()
	data = JSONField()

	def save(self, *args, **kwargs):
		'''on save update timestamps '''
		if not self.id:
			self.created =timezone.now()
		self.modified = timezone.now()
		return super(StationData, self).save(*args, **kwargs)

	class Meta:
		ordering = ['date']
		index_together = ['date','station_id', 'database']
		unique_together = (('station_id', 'date'),)


class Stations(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	station = models.CharField(max_length=100)
	name = models.CharField(max_length=100)
	database = models.CharField(max_length=5)
	code = models.CharField(max_length=100) # must not be in plain
	sensors = JSONField() # {'code': name}
	inactive_sensors = JSONField()

class Settings(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, primary_key=True)
	calc_color = JSONField()
	sensor_color = JSONField()
	calc_graph = JSONField()
	sensor_graph = JSONField()
	cportions = JSONField()
	chours = JSONField()
	ddays = JSONField()
	arain = JSONField()
	# new_alert = models.NullBooleanField()
	alert_mark_off = models.DateTimeField(null=True)

class Unit(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL)
	sensor_id = models.CharField(max_length=100)
	sensor_unit = models.CharField(max_length=100)
	class Meta:
		unique_together = (('sensor_id', 'sensor_unit'),)

class Alerts(models.Model):
	uid = models.CharField(max_length=36)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	name = models.CharField(max_length=100)
	description = models.CharField(max_length=100)
	sensors = JSONField()
	extract = models.CharField(max_length=16, default=None, null=True)
	logic = models.CharField(max_length=10)
	threshold = models.IntegerField()
	message = models.CharField(max_length=300)
	calc = models.CharField(max_length=30)
	type = models.CharField(max_length=20)
	email_alert = models.BooleanField()
	sms_alert = models.BooleanField()
	t_beyond = models.IntegerField(default=0)
	snooze = models.BooleanField(default=False)
	snooze_time = models.IntegerField(default=4)
	class Meta:
		# unique_together = (('sensors', 'logic', 'threshold', 'user'),('user', 'calc', 'logic', 'threshold'), ('user', 'calc', 'logic', 'threshold', 'sensors'))
		index_together = ['sensors', 'logic', 'threshold']

class AlertEvents(models.Model):
	created = models.DateTimeField(editable=False)
	modified = models.DateTimeField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	alert = models.ForeignKey(Alerts, on_delete=models.CASCADE)
	read = models.BooleanField()
	sent = models.BooleanField()
	time = models.DateTimeField()
	value = models.FloatField()
	event_id = models.CharField(max_length=100)
	widget = models.CharField(max_length=100)
	station = models.CharField(max_length=300)
	sensor = models.CharField(max_length=300)
	sensor_id = models.CharField(max_length=100)
	calc = models.CharField(max_length=20)
	notify = models.BooleanField()
	t_notify = models.DateTimeField()
	snoozed = models.BooleanField(default=False)

	def save(self, *args, **kwargs):
		'''on save update timestamps '''
		if not self.id:
			self.created =timezone.now()
		self.modified = timezone.now()
		return super(AlertEvents, self).save(*args, **kwargs)

	class Meta:
		ordering = ['t_notify']
		unique_together = (('user', 'alert', 'widget', 't_notify', 'sensor'))

# class Test(models.Model):
# 	name = JSONField()
# 	desc = JSONField()

class SMTPConfig(models.Model):
	use_this = models.BooleanField(primary_key=True)
	server_address = models.CharField(max_length=300)
	port = models.IntegerField()
	username = models.EmailField()
	password = models.CharField(max_length=100)
	ssl = models.BooleanField()
	tls = models.BooleanField()
	esmtp = models.BooleanField()

class EmailNotification(models.Model):
	created = models.DateTimeField(editable=False)
	modified = models.DateTimeField()
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	subject = models.CharField(max_length=100)
	content = models.CharField(max_length=500)
	success = models.BooleanField()
	error = models.CharField(max_length=100, default=' ')
	def save(self, *args, **kwargs):
		'''on save update timestamps '''
		if not self.id:
			self.created =timezone.now()
		self.modified = timezone.now()
		return super(EmailNotification, self).save(*args, **kwargs)

class SMSNotification(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	subject = models.CharField(max_length=100)
	content = models.CharField(max_length=500)
	success = models.BooleanField()
	error = models.CharField(max_length=100, default=' ')

class Dashboard(models.Model):
	uid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	name = models.CharField(max_length=50)
	active = models.BooleanField(default=False)

	class Meta:
		ordering = ['name']

class Data(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
	name = models.CharField(max_length=50)
	widget = models.ForeignKey(Widgets, related_name='dataset')
	function = models.CharField(max_length=50)
	sensor = models.CharField(max_length=100, null=True)
	extract = models.CharField(max_length=50)
	chart = models.ForeignKey(Widgets, null=True)
	date_from = models.DateTimeField(null=True)
	date_to = models.DateTimeField(null=True)
	value = models.FloatField(null=True)
	unit = models.CharField(max_length=10)
	stale = models.BooleanField(default=False)

def get_file_path(instance, filename):
	return 'files/{0}/{1}'.format(instance.user.username, filename)

class MapWidget(models.Model):
	wid = models.CharField(max_length=6, primary_key=True)
	index = models.IntegerField(default=0)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	name = models.CharField(max_length=50, default="New map widget")
	dashboard = models.ForeignKey('Dashboard')
	zoom = models.FloatField()
	latitude = models.FloatField()
	longitude = models.FloatField()
	tile_source = models.ForeignKey('MapTileSource')
	expand = models.BooleanField(default=False)
	class Meta:
		ordering = ['index']

class MapTileSource(models.Model):
	name = models.CharField(max_length=50, primary_key=True)
	url = models.CharField(max_length=500)
	attribution = models.CharField(max_length=300)

class File(models.Model):
	fid = models.UUIDField(primary_key=True, default=uuid.uuid4)
	user = models.ForeignKey(settings.AUTH_USER_MODEL)
	file = models.FileField(upload_to=get_file_path)

class Feature(models.Model):
	fid = models.UUIDField(primary_key=True, default=uuid.uuid4)
	name = models.CharField(max_length=100)
	geom_type = models.CharField(max_length=100)
	widget = ForeignKey('MapWidget')
	feature = JSONField()

class FeatureStat(models.Model):
	fsid = models.UUIDField(primary_key=True, default=uuid.uuid4)
	feature = models.ForeignKey('Feature')
	widget = models.ForeignKey('Widgets', null=True)
	data = models.ForeignKey('Data', null=True)
	stat_type = models.CharField(max_length=1, choices=(('s', 'Stat'),('p', 'PAW')))
	value = models.FloatField()

@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)

@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `File` object is updated
    with new file.
    """
    if not instance.fid:
        return False

    try:
        old_file = File.objects.get(fid=instance.fid).file
    except File.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


