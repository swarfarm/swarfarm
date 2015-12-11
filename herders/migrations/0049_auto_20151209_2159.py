# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0048_auto_20151208_0947'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_magic_mats_high',
            new_name='awaken_mats_magic_high',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_magic_mats_low',
            new_name='awaken_mats_magic_low',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_magic_mats_mid',
            new_name='awaken_mats_magic_mid',
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_dark_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_dark_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_dark_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_fire_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_fire_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_fire_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_light_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_light_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_light_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_water_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_water_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_water_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_wind_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_wind_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_wind_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='farmable',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monster',
            name='skill_ups_to_max',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
