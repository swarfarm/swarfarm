# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0105_monster_summonerswarmonsters_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='summoner',
            name='storage_dark_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_dark_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_dark_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_fire_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_fire_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_fire_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_light_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_light_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_light_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_magic_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_magic_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_magic_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_water_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_water_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_water_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_wind_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_wind_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_wind_mid',
        ),
    ]
