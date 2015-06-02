# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0024_auto_20150601_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summoner',
            name='public',
            field=models.BooleanField(default=False),
        ),
    ]
