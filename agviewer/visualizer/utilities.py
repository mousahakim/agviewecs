from __future__ import division
import datetime, time
from datetime import timedelta
from django.utils import timezone


def parse_date(date_string):
	frmt = '%Y-%m-%d %H:%M:%S'
	return datetime.datetime.strptime(date_string, frmt)

def dayofyear(date_string):
	frmt = '%Y-%m-%d %H:%M:%S'
	return datetime.datetime.strptime(date_string, frmt).timetuple().tm_yday

def decatime(seconds):
	DIFF = 946684800
	return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(int(seconds)+DIFF))

