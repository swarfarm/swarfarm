# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0081_auto_20160420_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summoner',
            name='global_server',
        ),
        migrations.AddField(
            model_name='summoner',
            name='server',
            field=models.IntegerField(default=0, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')]),
        ),
    ]
