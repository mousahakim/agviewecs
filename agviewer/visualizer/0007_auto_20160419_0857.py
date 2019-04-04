# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('visualizer', '0006_auto_20160419_0855'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appuser',
            name='fc_salt',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='appuser',
            name='user',
            field=models.OneToOneField(primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
