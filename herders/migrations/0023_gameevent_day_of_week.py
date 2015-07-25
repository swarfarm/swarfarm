# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0022_auto_20150724_1653'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameevent',
            name='day_of_week',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Sunday'), (1, b'Monday'), (2, b'Tuesday'), (3, b'Wednesday'), (4, b'Thursday'), (5, b'Friday'), (6, b'Saturday')]),
        ),
    ]
