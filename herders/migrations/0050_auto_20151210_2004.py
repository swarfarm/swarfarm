# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0049_auto_20151209_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_mid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_dark_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_dark_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_dark_mid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_fire_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_fire_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_fire_mid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_light_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_light_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_light_mid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_magic_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_magic_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_magic_mid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_water_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_water_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_water_mid',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_wind_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_wind_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_wind_mid',
            field=models.IntegerField(default=0),
        ),
    ]
