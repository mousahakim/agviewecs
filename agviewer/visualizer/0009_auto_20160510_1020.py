# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('visualizer', '0008_files'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chip',
            options={'ordering': ['date']},
        ),
        migrations.AddField(
            model_name='chip',
            name='user',
            field=models.ForeignKey(default='', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
