# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0050_auto_20151210_2004'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterSkillScalesWith',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('multiplier', models.IntegerField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MonsterSkillScalingStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stat', models.CharField(max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='atk_multiplier',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_dark_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_dark_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_dark_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_fire_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_fire_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_fire_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_light_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_light_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_light_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_magic_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_magic_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_magic_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_water_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_water_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_water_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_wind_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_wind_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_mats_wind_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskillscaleswith',
            name='monsterskill',
            field=models.ForeignKey(to='herders.MonsterSkill'),
        ),
        migrations.AddField(
            model_name='monsterskillscaleswith',
            name='scalingstat',
            field=models.ForeignKey(to='herders.MonsterSkillScalingStat'),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='scales_with',
            field=models.ManyToManyField(to='herders.MonsterSkillScalingStat', through='herders.MonsterSkillScalesWith'),
        ),
    ]
