# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0023_auto_20150525_0101'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monsterinstance',
            options={'ordering': ['-stars', '-level', '-priority', 'monster__name']},
        ),
        migrations.AlterField(
            model_name='summoner',
            name='global_server',
            field=models.NullBooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='public',
            field=models.NullBooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='summoner_name',
            field=models.CharField(max_length=256, null=True, blank=True),
        ),
    ]
