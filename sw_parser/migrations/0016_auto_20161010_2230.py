# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0015_auto_20161010_2223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runlog',
            name='server',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')]),
        ),
        migrations.AlterField(
            model_name='summonlog',
            name='server',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')]),
        ),
    ]
