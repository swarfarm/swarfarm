# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0014_auto_20161010_2200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runlog',
            name='clear_time',
            field=models.DurationField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runlog',
            name='crystal',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runlog',
            name='mana',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runlog',
            name='timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='summonlog',
            name='timestamp',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
