# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0024_gameevent_all_day'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameevent',
            name='end_time',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='gameevent',
            name='start_time',
            field=models.TimeField(null=True, blank=True),
        ),
    ]
