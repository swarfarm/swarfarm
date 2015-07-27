# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0025_auto_20150724_1701'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameevent',
            name='day_of_week',
            field=models.IntegerField(blank=True, null=True, choices=[(6, b'Sunday'), (0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday')]),
        ),
    ]
