# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0020_auto_20150724_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameevent',
            name='element_affinity',
            field=models.CharField(max_length=10, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')]),
        ),
        migrations.AddField(
            model_name='gameevent',
            name='timezone',
            field=timezone_field.fields.TimeZoneField(default=b'America/Los_Angeles'),
        ),
        migrations.AlterField(
            model_name='gameevent',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='gameevent',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='gameevent',
            name='link',
            field=models.TextField(null=True, blank=True),
        ),
    ]
