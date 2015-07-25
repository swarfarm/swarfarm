# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0021_auto_20150724_1650'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameevent',
            name='end_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='gameevent',
            name='start_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='gameevent',
            name='end_time',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='gameevent',
            name='start_time',
            field=models.TimeField(),
        ),
    ]
