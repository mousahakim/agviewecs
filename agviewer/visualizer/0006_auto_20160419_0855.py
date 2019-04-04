# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('visualizer', '0005_dstationlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='appuser',
            name='dg_password',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='appuser',
            name='dg_username',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
