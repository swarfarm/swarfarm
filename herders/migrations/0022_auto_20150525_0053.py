# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0021_auto_20150525_0044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summoner',
            name='storage_dark_high',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_dark_low',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_dark_mid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_fire_high',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_fire_low',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_fire_mid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_light_high',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_light_low',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_light_mid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_magic_high',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_magic_low',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_magic_mid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_water_high',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_water_low',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_water_mid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_wind_high',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_wind_low',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='summoner',
            name='storage_wind_mid',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
