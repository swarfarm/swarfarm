# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0082_auto_20160426_2021'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summoner',
            name='server',
            field=models.IntegerField(default=0, null=True, blank=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')]),
        ),
    ]
