# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0025_auto_20150601_2239'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summoner',
            name='rep_monster',
        ),
    ]
