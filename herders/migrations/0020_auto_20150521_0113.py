# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0019_auto_20150509_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='summoner',
            name='rep_monster',
            field=models.ForeignKey(blank=True, to='herders.MonsterInstance', null=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_dark_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_dark_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_dark_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_fire_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_fire_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_fire_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_light_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_light_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_light_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_magic_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_magic_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_magic_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_water_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_water_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_water_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_wind_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_wind_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='storage_wind_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
