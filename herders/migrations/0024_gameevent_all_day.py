# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0023_gameevent_day_of_week'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameevent',
            name='all_day',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
