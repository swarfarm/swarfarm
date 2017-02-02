# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0081_auto_20160420_1551'),
        ('sw_parser', '0002_auto_20160421_0957'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dungeon',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='runlog',
            name='summoner',
            field=models.ForeignKey(blank=True, to='herders.Summoner', null=True),
        ),
        migrations.AddField(
            model_name='summonlog',
            name='summoner',
            field=models.ForeignKey(blank=True, to='herders.Summoner', null=True),
        ),
    ]
