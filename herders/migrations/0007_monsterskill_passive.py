# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0006_monsterskill_slot'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskill',
            name='passive',
            field=models.BooleanField(default=False),
        ),
    ]
