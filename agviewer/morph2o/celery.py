from __future__ import absolute_import, unicode_literals
from datetime import timedelta
#from visualizer import tasks
import os, django

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'morph2o.settings')


django.setup()
#from django.conf import settings  # noqa

#settings.configure()
# Using RabbitMQ
# app = Celery('morph2o', broker='pyamqp://admin:Rah3lajan@10.0.0.151:5672', task_ignore_result=True, task_time_limit=20)
# Using Redis
app = Celery('morph2o', broker='redis://10.0.0.173:6379/0', task_ignore_result=True)

# Using a string here means the worker will not have to
# pickle the object when using Windows.
# app.conf.update(
# 	CELERY_RESULT_BACKEND='django-db',)
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()
app.conf.beat_schedule = {
#     'hourly-download': {
#         'task': 'visualizer.tasks.download',
#         'schedule': 3600.0
#     },
    'hourly-async-download': {
        'task': 'visualizer.tasks.async_download',
        'schedule': 900.0
    },
    'hourly-async-update':{
        'task': 'visualizer.tasks.async_update',
        'schedule': 900.0
    },
}
#app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
