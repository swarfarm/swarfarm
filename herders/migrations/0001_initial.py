# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import timezone_field.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('element', models.CharField(max_length=10)),
                ('base_stars', models.IntegerField()),
                ('awaken_ele_mats_small', models.IntegerField()),
                ('awaken_ele_mats_med', models.IntegerField()),
                ('awaken_ele_mats_large', models.IntegerField()),
                ('awaken_magic_mats_small', models.IntegerField()),
                ('awaken_magic_mats_med', models.IntegerField()),
                ('awaken_magic_mats_large', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='MonsterInstance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stars', models.IntegerField()),
                ('level', models.IntegerField()),
                ('skill_1_level', models.IntegerField()),
                ('skill_2_level', models.IntegerField()),
                ('skill_3_level', models.IntegerField()),
                ('skill_4_level', models.IntegerField()),
                ('monster', models.ForeignKey(to='herders.Monster')),
            ],
        ),
        migrations.CreateModel(
            name='MonsterSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('skill_number', models.IntegerField()),
                ('max_level', models.IntegerField()),
                ('icon_path', models.CharField(max_length=100)),
                ('monster', models.ForeignKey(to='herders.Monster')),
            ],
        ),
        migrations.CreateModel(
            name='Summoner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summoner_name', models.CharField(max_length=256)),
                ('global_server', models.BooleanField(default=True)),
                ('public', models.BooleanField(default=False)),
                ('timezone', timezone_field.fields.TimeZoneField(default=b'America/Los_Angeles')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner'),
        ),
    ]
