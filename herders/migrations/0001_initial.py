# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import timezone_field.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Fusion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stars', models.IntegerField()),
                ('cost', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('image_filename', models.CharField(max_length=250, null=True, blank=True)),
                ('element', models.CharField(default=b'fire', max_length=6, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')])),
                ('archetype', models.CharField(default=b'attack', max_length=10, choices=[(b'attack', b'Attack'), (b'hp', b'HP'), (b'support', b'Support'), (b'defense', b'Defense'), (b'material', b'Material')])),
                ('base_stars', models.IntegerField(choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)])),
                ('can_awaken', models.BooleanField(default=True)),
                ('is_awakened', models.BooleanField(default=False)),
                ('awaken_ele_mats_low', models.IntegerField(null=True, blank=True)),
                ('awaken_ele_mats_mid', models.IntegerField(null=True, blank=True)),
                ('awaken_ele_mats_high', models.IntegerField(null=True, blank=True)),
                ('awaken_magic_mats_low', models.IntegerField(null=True, blank=True)),
                ('awaken_magic_mats_mid', models.IntegerField(null=True, blank=True)),
                ('awaken_magic_mats_high', models.IntegerField(null=True, blank=True)),
                ('fusion_food', models.BooleanField(default=False)),
                ('awakens_from', models.ForeignKey(related_name='+', blank=True, to='herders.Monster', null=True)),
                ('awakens_to', models.ForeignKey(related_name='+', blank=True, to='herders.Monster', null=True)),
            ],
            options={
                'ordering': ['name', 'element'],
            },
        ),
        migrations.CreateModel(
            name='MonsterInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('stars', models.IntegerField()),
                ('level', models.IntegerField()),
                ('skill_1_level', models.IntegerField(null=True, blank=True)),
                ('skill_2_level', models.IntegerField(null=True, blank=True)),
                ('skill_3_level', models.IntegerField(null=True, blank=True)),
                ('skill_4_level', models.IntegerField(null=True, blank=True)),
                ('fodder', models.BooleanField(default=False)),
                ('in_storage', models.BooleanField(default=False)),
                ('priority', models.IntegerField(default=2, choices=[(0, b'Done'), (1, b'Low'), (2, b'Medium'), (3, b'High')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('monster', models.ForeignKey(to='herders.Monster')),
            ],
            options={
                'ordering': ['-stars', '-level', '-priority', 'monster__name'],
            },
        ),
        migrations.CreateModel(
            name='MonsterSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('dungeon_leader', models.BooleanField(default=False)),
                ('arena_leader', models.BooleanField(default=False)),
                ('guild_leader', models.BooleanField(default=False)),
                ('max_level', models.IntegerField()),
                ('level_progress_description', models.TextField()),
                ('icon_filename', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='MonsterSkillEffects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_buff', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('icon_filename', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='RuneInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('type', models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire')])),
                ('stars', models.IntegerField()),
                ('level', models.IntegerField()),
                ('slot', models.IntegerField()),
                ('main_stat', models.IntegerField(choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('main_stat_value', models.IntegerField(default=0)),
                ('innate_stat', models.IntegerField(blank=True, null=True, choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('innate_stat_value', models.IntegerField(null=True, blank=True)),
                ('substat_1', models.IntegerField(blank=True, null=True, choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('substat_1_value', models.IntegerField(null=True, blank=True)),
                ('substat_2', models.IntegerField(blank=True, null=True, choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('substat_2_value', models.IntegerField(null=True, blank=True)),
                ('substat_3', models.IntegerField(blank=True, null=True, choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('substat_3_value', models.IntegerField(null=True, blank=True)),
                ('substat_4', models.IntegerField(blank=True, null=True, choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('substat_4_value', models.IntegerField(null=True, blank=True)),
                ('monster', models.ForeignKey(blank=True, to='herders.MonsterInstance', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Summoner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summoner_name', models.CharField(max_length=256, null=True, blank=True)),
                ('global_server', models.NullBooleanField(default=True)),
                ('public', models.BooleanField(default=False)),
                ('timezone', timezone_field.fields.TimeZoneField(default=b'America/Los_Angeles')),
                ('notes', models.TextField(null=True, blank=True)),
                ('storage_magic_low', models.IntegerField(default=0)),
                ('storage_magic_mid', models.IntegerField(default=0)),
                ('storage_magic_high', models.IntegerField(default=0)),
                ('storage_fire_low', models.IntegerField(default=0)),
                ('storage_fire_mid', models.IntegerField(default=0)),
                ('storage_fire_high', models.IntegerField(default=0)),
                ('storage_water_low', models.IntegerField(default=0)),
                ('storage_water_mid', models.IntegerField(default=0)),
                ('storage_water_high', models.IntegerField(default=0)),
                ('storage_wind_low', models.IntegerField(default=0)),
                ('storage_wind_mid', models.IntegerField(default=0)),
                ('storage_wind_high', models.IntegerField(default=0)),
                ('storage_light_low', models.IntegerField(default=0)),
                ('storage_light_mid', models.IntegerField(default=0)),
                ('storage_light_high', models.IntegerField(default=0)),
                ('storage_dark_low', models.IntegerField(default=0)),
                ('storage_dark_mid', models.IntegerField(default=0)),
                ('storage_dark_high', models.IntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('favorite', models.BooleanField(default=False)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TeamGroup',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('owner', models.ForeignKey(to='herders.Summoner')),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='group',
            field=models.ForeignKey(to='herders.TeamGroup'),
        ),
        migrations.AddField(
            model_name='team',
            name='roster',
            field=models.ManyToManyField(to='herders.MonsterInstance'),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner'),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='skill_effect',
            field=models.ManyToManyField(to='herders.MonsterSkillEffects'),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner'),
        ),
        migrations.AddField(
            model_name='monster',
            name='skills',
            field=models.ManyToManyField(to='herders.MonsterSkill'),
        ),
        migrations.AddField(
            model_name='fusion',
            name='ingredients',
            field=models.ManyToManyField(to='herders.Monster'),
        ),
        migrations.AddField(
            model_name='fusion',
            name='product',
            field=models.ForeignKey(related_name='product', to='herders.Monster'),
        ),
    ]
