from django.contrib import admin

# from .models import Question

# admin.site.register(Question)

# Register your models here.

from visualizer.models import AppUser, SensorCodes, SMTPConfig, AlertEvents, EmailNotification, SMSNotification, MapTileSource

@admin.register(AppUser)
class AppUserAdmin(admin.ModelAdmin):
	list_display = ('user', 'fc_username', 'dg_username')


@admin.register(SensorCodes)
class SensorCodesAdmin(admin.ModelAdmin):
	list_display = ('user', 'sensor_id', 'sensor_name', 'sensor_unit', 'axis_code', 'axis_name')

@admin.register(SMTPConfig)
class SMTPConfigAdmin(admin.ModelAdmin):
	list_display = ('username', 'server_address', 'use_this')

@admin.register(AlertEvents)
class AlertEventsAdmin(admin.ModelAdmin):
	list_display = ('user', 'time', 't_notify', 'notify', 'widget', 'alert')

@admin.register(EmailNotification)
class EmailNotificationAdmin(admin.ModelAdmin):
	list_display = ('user', 'subject', 'success', 'error')

@admin.register(SMSNotification)
class SMSNotificationAdmin(admin.ModelAdmin):
	list_display = ('user', 'subject', 'success', 'error')

@admin.register(MapTileSource)
class MapTileSourceAdmin(admin.ModelAdmin):
	list_display = ('name', 'url', 'attribution')