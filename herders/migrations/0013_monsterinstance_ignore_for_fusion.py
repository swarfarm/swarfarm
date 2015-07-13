# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0012_auto_20150708_2254'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterinstance',
            name='ignore_for_fusion',
            field=models.BooleanField(default=False),
        ),
    ]
