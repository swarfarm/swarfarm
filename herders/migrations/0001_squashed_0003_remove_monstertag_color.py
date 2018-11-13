# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
from django.conf import settings
import timezone_field.fields
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
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
                ('awaken_magic_mats_low', models.IntegerField(null=True, blank=True)),
                ('awaken_magic_mats_mid', models.IntegerField(null=True, blank=True)),
                ('awaken_magic_mats_high', models.IntegerField(null=True, blank=True)),
                ('fusion_food', models.BooleanField(default=False)),
                ('awakens_from', models.ForeignKey(related_name='+', on_delete=models.SET_NULL, blank=True, to='herders.Monster', null=True)),
                ('awakens_to', models.ForeignKey(related_name='+', on_delete=models.SET_NULL, blank=True, to='herders.Monster', null=True)),
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
                ('monster', models.ForeignKey(to='herders.Monster', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-stars', '-level', '-priority', 'monster__name'],
            },
        ),
        migrations.CreateModel(
            name='MonsterSkillEffect',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_buff', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('icon_filename', models.CharField(max_length=100, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='MonsterSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('max_level', models.IntegerField()),
                ('level_progress_description', models.TextField(null=True, blank=True)),
                ('icon_filename', models.CharField(max_length=100, null=True, blank=True)),
                ('skill_effect', models.ManyToManyField(to='herders.MonsterSkillEffect', blank=True)),
                ('slot', models.IntegerField(default=1)),
                ('passive', models.BooleanField(default=False)),
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
            ],
        ),
        migrations.CreateModel(
            name='Summoner',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('summoner_name', models.CharField(max_length=256, null=True, blank=True)),
                ('public', models.BooleanField(default=False)),
                ('timezone', timezone_field.fields.TimeZoneField(default='America/Los_Angeles')),
                ('notes', models.TextField(null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
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
                ('owner', models.ForeignKey(to='herders.Summoner', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='group',
            field=models.ForeignKey(to='herders.TeamGroup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='team',
            name='roster',
            field=models.ManyToManyField(to='herders.MonsterInstance'),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='monster',
            name='skills',
            field=models.ManyToManyField(to='herders.MonsterSkill', blank=True),
        ),
        migrations.AddField(
            model_name='fusion',
            name='ingredients',
            field=models.ManyToManyField(to='herders.Monster'),
        ),
        migrations.AddField(
            model_name='fusion',
            name='product',
            field=models.ForeignKey(related_name='product', to='herders.Monster', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='team',
            name='leader',
            field=models.ForeignKey(related_name='team_leader', on_delete=models.SET_NULL, blank=True, to='herders.MonsterInstance', null=True),
        ),
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='teamgroup',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='team',
            name='roster',
            field=models.ManyToManyField(to='herders.MonsterInstance', blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_hp',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='accuracy',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_attack',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='crit_damage',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='crit_rate',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_defense',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='resistance',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='speed',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='ignore_for_fusion',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='monsterskill',
            options={'ordering': ['name', 'icon_filename']},
        ),
        migrations.AlterModelOptions(
            name='monsterskilleffect',
            options={'ordering': ['-is_buff', 'name']},
        ),
        migrations.CreateModel(
            name='MonsterLeaderSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attribute', models.IntegerField(choices=[(1, b'HP'), (2, b'Attack Power'), (3, b'Defense'), (4, b'Attack Speed'), (5, b'Critical Rate'), (6, b'Critical Damage'), (7, b'Resistance'), (8, b'Accuracy')])),
                ('amount', models.IntegerField()),
                ('element', models.CharField(blank=True, max_length=6, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')])),
            ],
        ),
        migrations.AddField(
            model_name='monster',
            name='leader_skill',
            field=models.ForeignKey(blank=True, to='herders.MonsterLeaderSkill', null=True, on_delete=models.SET_NULL),
        ),
        migrations.AlterModelOptions(
            name='monsterleaderskill',
            options={'ordering': ['attribute', 'amount', 'element']},
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_bonus',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='monsterleaderskill',
            name='attribute',
            field=models.IntegerField(choices=[(1, b'HP'), (2, b'Attack Power'), (3, b'Defense'), (4, b'Attack Speed'), (5, b'Critical Rate'), (6, b'Resistance'), (7, b'Accuracy')]),
        ),
        migrations.AlterField(
            model_name='monsterleaderskill',
            name='attribute',
            field=models.IntegerField(choices=[(1, b'HP'), (2, b'Attack Power'), (3, b'Defense'), (4, b'Attack Speed'), (5, b'Critical Rate'), (6, b'Resistance'), (7, b'Accuracy'), (8, b'Critical DMG')]),
        ),
        migrations.CreateModel(
            name='GameEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('type', models.IntegerField(choices=[(1, b'Elemental Dungeon'), (2, b'Special Event')])),
                ('description', models.TextField(null=True, blank=True)),
                ('link', models.TextField(null=True, blank=True)),
                ('start_time', models.TimeField(null=True, blank=True)),
                ('end_time', models.TimeField(null=True, blank=True)),
                ('element_affinity', models.CharField(max_length=10, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')])),
                ('timezone', timezone_field.fields.TimeZoneField(default='America/Los_Angeles')),
                ('end_date', models.DateField(null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('day_of_week', models.IntegerField(blank=True, null=True, choices=[(6, b'Sunday'), (0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday')])),
                ('all_day', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='MonsterSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('icon_filename', models.CharField(max_length=100, null=True, blank=True)),
                ('farmable_source', models.BooleanField(default=False)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='monster',
            name='source',
            field=models.ManyToManyField(to='herders.MonsterSource', blank=True),
        ),
        migrations.AlterModelOptions(
            name='monstersource',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='monster',
            name='obtainable',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterModelOptions(
            name='fusion',
            options={'ordering': ['meta_order']},
        ),
        migrations.AlterModelOptions(
            name='monstersource',
            options={'ordering': ['meta_order', 'icon_filename', 'name']},
        ),
        migrations.AddField(
            model_name='fusion',
            name='meta_order',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='monstersource',
            name='meta_order',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AlterModelOptions(
            name='monsterskill',
            options={'ordering': ['slot', 'name']},
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_1_level',
            field=models.IntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_2_level',
            field=models.IntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_3_level',
            field=models.IntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_4_level',
            field=models.IntegerField(default=1, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='following',
            field=models.ManyToManyField(related_name='followed_by', to='herders.Summoner'),
        ),
        migrations.AddField(
            model_name='monster',
            name='summonerswar_co_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='wikia_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='assigned_to',
            field=models.ForeignKey(blank=True, to='herders.MonsterInstance', null=True, on_delete=models.SET_NULL),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_accuracy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_atk',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_crit_dmg',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_crit_rate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_def',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_hp',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_resist',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_speed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monster',
            name='bestiary_slug',
            field=models.SlugField(max_length=255, null=True, editable=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='quality',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterModelOptions(
            name='runeinstance',
            options={'ordering': ['type', 'slot', 'level', 'quality']},
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='quality',
            field=models.IntegerField(default=0, choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='type',
            field=models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy')]),
        ),
        migrations.AddField(
            model_name='monsterleaderskill',
            name='area',
            field=models.IntegerField(default=1, choices=[(1, b'General'), (2, b'Dungeon'), (3, b'Element'), (4, b'Arena'), (5, b'Guild')]),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='notes',
            field=models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='description',
            field=models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled', null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_accuracy',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_attack',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_crit_damage',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_crit_rate',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_defense',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_hp',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_resistance',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_speed',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_accuracy',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_attack',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_crit_damage',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_crit_rate',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_defense',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_hp',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_resistance',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_speed',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='base_stars',
            field=models.IntegerField(choices=[(1, b'1<span class="glyphicon glyphicon-star"></span>'), (2, b'2<span class="glyphicon glyphicon-star"></span>'), (3, b'3<span class="glyphicon glyphicon-star"></span>'), (4, b'4<span class="glyphicon glyphicon-star"></span>'), (5, b'5<span class="glyphicon glyphicon-star"></span>'), (6, b'6<span class="glyphicon glyphicon-star"></span>')]),
        ),
        migrations.AddField(
            model_name='monster',
            name='max_lvl_attack',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='max_lvl_defense',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='max_lvl_hp',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_bonus_content_id',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_bonus_content_type',
            field=models.ForeignKey(related_name='content_type_awaken_bonus', on_delete=models.SET_NULL, blank=True, to='contenttypes.ContentType', null=True),
        ),
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
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_dark_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_dark_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_fire_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_fire_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_fire_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_light_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_light_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_light_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_water_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_water_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_water_mid',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_wind_high',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_wind_low',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_mats_wind_mid',
            field=models.IntegerField(default=0, blank=True),
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
        migrations.CreateModel(
            name='MonsterSkillScalingStat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stat', models.CharField(max_length=20)),
                ('com2us_desc', models.CharField(max_length=30, null=True, blank=True)),
                ('description', models.TextField(null=True, blank=True)),
            ],
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
        migrations.AddField(
            model_name='monsterskill',
            name='cooltime',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterModelOptions(
            name='monsterinstance',
            options={'ordering': ['-stars', '-level', 'monster__name']},
        ),
        migrations.AlterModelOptions(
            name='runeinstance',
            options={'ordering': ['slot', 'type', 'level', 'quality']},
        ),
        migrations.AddField(
            model_name='monster',
            name='com2us_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='com2us_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='com2us_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='com2us_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='MonsterPiece',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('pieces', models.IntegerField(default=0)),
                ('monster', models.ForeignKey(to='herders.Monster', on_delete=models.CASCADE)),
                ('owner', models.ForeignKey(to='herders.Summoner', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['monster__name'],
            },
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='created',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='MonsterSkillEffectDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aoe', models.BooleanField(default=False, help_text=b'Effect applies to entire friendly or enemy group')),
                ('single_target', models.BooleanField(default=False, help_text=b'Effect applies to a single monster')),
                ('self_effect', models.BooleanField(default=False, help_text=b'Effect applies to the monster using the skill')),
                ('quantity', models.IntegerField(help_text=b'Number of items this effect affects on the target', null=True, blank=True)),
                ('all', models.BooleanField(default=False, help_text=b'This effect affects all items on the target')),
                ('effect', models.ForeignKey(to='herders.MonsterSkillEffect', on_delete=models.CASCADE)),
                ('skill', models.ForeignKey(to='herders.MonsterSkill', on_delete=models.CASCADE)),
                ('random', models.BooleanField(default=False, help_text=b'Skill effect applies randomly to the target')),
                ('chance', models.IntegerField(help_text=b'Chance of effect occuring per hit', null=True, blank=True)),
                ('on_crit', models.BooleanField(default=False)),
                ('on_death', models.BooleanField(default=False)),
                ('note', models.TextField(help_text=b"Explain anything else that doesn't fit in other fields", null=True, blank=True)),
                ('self_hp', models.BooleanField(default=False, help_text=b"Amount of this effect is based on casting monster's HP")),
                ('target_hp', models.BooleanField(default=False, help_text=b"Amount of this effect is based on target monster's HP")),
                ('damage', models.BooleanField(default=False, help_text=b'Amount of this effect is based on damage dealt')),
            ],
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='effect',
            field=models.ManyToManyField(related_name='effect', through='herders.MonsterSkillEffectDetail', to='herders.MonsterSkillEffect', blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='marked_for_sale',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='value',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='com2us_id',
            field=models.BigIntegerField(default=None, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='hits',
            field=models.IntegerField(default=1, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='aoe',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='MonsterTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
            ],
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='tags',
            field=models.ManyToManyField(to='herders.MonsterTag', blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='priority',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Low'), (2, b'Medium'), (3, b'High')]),
        ),
        migrations.AlterModelOptions(
            name='monstertag',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='monstertag',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.CreateModel(
            name='RuneCraftInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('com2us_id', models.BigIntegerField(null=True, blank=True)),
                ('type', models.IntegerField(choices=[(0, b'Grindstone'), (1, b'Enchant Gem')])),
                ('rune', models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy'), (17, b'Fight'), (18, b'Determination'), (19, b'Enhance'), (20, b'Accuracy'), (21, b'Tolerance')])),
                ('stat', models.IntegerField(choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('quality', models.IntegerField(choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')])),
                ('value', models.IntegerField(null=True, blank=True)),
                ('owner', models.ForeignKey(to='herders.Summoner', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_1_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_2_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_3_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_4_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
        migrations.AlterModelOptions(
            name='monsterskilleffect',
            options={},
        ),
        migrations.AlterModelOptions(
            name='monsterskilleffect',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='summoner',
            name='server',
            field=models.IntegerField(default=0, null=True, blank=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')]),
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('com2us_id', models.IntegerField()),
                ('max_level', models.IntegerField()),
                ('area', models.IntegerField(blank=True, null=True, choices=[(0, b'Everywhere'), (1, b'Guild Battle')])),
                ('affected_stat', models.IntegerField(blank=True, null=True, choices=[(0, b'HP'), (1, b'ATK'), (2, b'DEF'), (3, b'SPD'), (4, b'CRI Rate'), (5, b'CRI Dmg'), (6, b'Resistance'), (7, b'Accuracy'), (8, b'Max. Energy'), (9, b'Mana Stone Storage'), (10, b'Mana Stone Production Rate'), (11, b'Energy Production Rate'), (12, b'Arcane Tower ATK'), (13, b'Arcane Tower SPD')])),
                ('element', models.CharField(blank=True, max_length=6, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')])),
                ('stat_bonus', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None)),
                ('upgrade_cost', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None)),
                ('icon_filename', models.CharField(max_length=100, null=True, blank=True)),
                ('name', models.CharField(default='', max_length=30)),
                ('description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('level', models.IntegerField()),
                ('owner', models.ForeignKey(to='herders.Summoner', on_delete=models.CASCADE)),
                ('building', models.ForeignKey(to='herders.Building', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='multiplier_formula',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='scaling_stats',
            field=models.ManyToManyField(to='herders.MonsterSkillScalingStat', blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='family_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='multiplier_formula_raw',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
        migrations.AlterModelOptions(
            name='monsterskillscalingstat',
            options={'ordering': ['stat']},
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='max_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='main_stat_value',
            field=models.IntegerField(),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_upgrades_remaining',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_crafts',
            field=django.contrib.postgres.fields.ArrayField(size=4, null=True, base_field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]), blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_values',
            field=django.contrib.postgres.fields.ArrayField(size=4, null=True, base_field=models.IntegerField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substats',
            field=django.contrib.postgres.fields.ArrayField(size=4, null=True, base_field=models.IntegerField(blank=True, null=True, choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')]), blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='avg_rune_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='type',
            field=models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy'), (17, b'Fight'), (18, b'Determination'), (19, b'Enhance'), (20, b'Accuracy'), (21, b'Tolerance')]),
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('magic_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Magic Essence', base_field=models.IntegerField(default=0), size=3)),
                ('fire_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Fire Essence', base_field=models.IntegerField(default=0), size=3)),
                ('water_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Water Essence', base_field=models.IntegerField(default=0), size=3)),
                ('wind_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Wind Essence', base_field=models.IntegerField(default=0), size=3)),
                ('light_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Light Essence', base_field=models.IntegerField(default=0), size=3)),
                ('dark_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Dark Essence', base_field=models.IntegerField(default=0), size=3)),
                ('wood', models.IntegerField(default=0, help_text=b'Hard Wood')),
                ('leather', models.IntegerField(default=0, help_text=b'Tough Leather')),
                ('rock', models.IntegerField(default=0, help_text=b'Solid Rock')),
                ('ore', models.IntegerField(default=0, help_text=b'Solid Iron Ore')),
                ('mithril', models.IntegerField(default=0, help_text=b'Shining Mythril')),
                ('cloth', models.IntegerField(default=0, help_text=b'Thick Cloth')),
                ('rune_piece', models.IntegerField(default=0, help_text=b'Rune Piece')),
                ('dust', models.IntegerField(default=0, help_text=b'Magic Dust')),
                ('symbol_harmony', models.IntegerField(default=0, help_text=b'Symbol of Harmony')),
                ('symbol_transcendance', models.IntegerField(default=0, help_text=b'Symbol of Transcendance')),
                ('symbol_chaos', models.IntegerField(default=0, help_text=b'Symbol of Chaos')),
                ('crystal_water', models.IntegerField(default=0, help_text=b'Frozen Water Crystal')),
                ('crystal_fire', models.IntegerField(default=0, help_text=b'Flaming Fire Crystal')),
                ('crystal_wind', models.IntegerField(default=0, help_text=b'Whirling Wind Crystal')),
                ('crystal_light', models.IntegerField(default=0, help_text=b'Shiny Light Crystal')),
                ('crystal_dark', models.IntegerField(default=0, help_text=b'Pitch-black Dark Crystal')),
                ('crystal_magic', models.IntegerField(default=0, help_text=b'Condensed Magic Crystal')),
                ('crystal_pure', models.IntegerField(default=0, help_text=b'Pure Magic Crystal')),
                ('owner', models.OneToOneField(to='herders.Summoner', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='CraftCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CraftMaterial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('com2us_id', models.IntegerField()),
                ('name', models.CharField(max_length=40)),
                ('icon_filename', models.CharField(max_length=100, null=True, blank=True)),
                ('sell_value', models.IntegerField(null=True, blank=True)),
                ('source', models.ManyToManyField(to='herders.MonsterSource', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='HomunculusSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mana_cost', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterModelOptions(
            name='monsterleaderskill',
            options={'ordering': ['attribute', 'amount', 'element'], 'verbose_name': 'Leader Skill', 'verbose_name_plural': 'Leader Skills'},
        ),
        migrations.AlterModelOptions(
            name='monsterskill',
            options={'ordering': ['slot', 'name'], 'verbose_name': 'Skill', 'verbose_name_plural': 'Skills'},
        ),
        migrations.AlterModelOptions(
            name='monsterskilleffect',
            options={'ordering': ['name'], 'verbose_name': 'Skill Effect', 'verbose_name_plural': 'Skill Effects'},
        ),
        migrations.AlterModelOptions(
            name='monsterskillscalingstat',
            options={'ordering': ['stat'], 'verbose_name': 'Scaling Stat', 'verbose_name_plural': 'Scaling Stats'},
        ),
        migrations.AddField(
            model_name='monster',
            name='craft_cost',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='homunculus',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='homunculusskill',
            name='monsters',
            field=models.ManyToManyField(to='herders.Monster'),
        ),
        migrations.AddField(
            model_name='homunculusskill',
            name='prerequisites',
            field=models.ManyToManyField(related_name='homunculus_prereq', to='herders.MonsterSkill', blank=True),
        ),
        migrations.AddField(
            model_name='homunculusskill',
            name='skill',
            field=models.ForeignKey(to='herders.MonsterSkill', on_delete=models.CASCADE),
        ),
        migrations.CreateModel(
            name='HomunculusSkillCraftCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('craft', models.ForeignKey(to='herders.CraftMaterial', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='MonsterCraftCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('craft', models.ForeignKey(to='herders.CraftMaterial', on_delete=models.CASCADE)),
                ('monster', models.ForeignKey(to='herders.Monster', on_delete=models.CASCADE)),
            ],
        ),
        migrations.DeleteModel(
            name='CraftCost',
        ),
        migrations.AddField(
            model_name='homunculusskillcraftcost',
            name='skill',
            field=models.ForeignKey(to='herders.HomunculusSkill', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='homunculusskill',
            name='craft_materials',
            field=models.ManyToManyField(to='herders.CraftMaterial', through='herders.HomunculusSkillCraftCost'),
        ),
        migrations.AddField(
            model_name='monster',
            name='craft_materials',
            field=models.ManyToManyField(to='herders.CraftMaterial', through='herders.MonsterCraftCost'),
        ),
        migrations.AddField(
            model_name='monster',
            name='summonerswarmonsters_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='original_quality',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
        migrations.AlterField(
            model_name='building',
            name='name',
            field=models.CharField(max_length=30),
        ),
    ]
