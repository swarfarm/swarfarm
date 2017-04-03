# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bestiary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterDrop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grade', models.IntegerField()),
                ('level', models.IntegerField()),
                ('monster', models.ForeignKey(to='bestiary.Monster')),
            ],
        ),
        migrations.CreateModel(
            name='RuneDrop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy')])),
                ('stars', models.IntegerField()),
                ('slot', models.IntegerField()),
                ('value', models.IntegerField()),
                ('max_efficiency', models.FloatField()),
                ('main_stat', models.IntegerField(choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('main_stat_value', models.IntegerField()),
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
            name='RunLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('server', models.IntegerField(choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia')])),
                ('dungeon', models.IntegerField(choices=[(0, b"Giant's Keep"), (1, b"Dragon's Lair"), (2, b'Necropolis'), (3, b'Hall of Magic'), (4, b'Hall of Fire'), (5, b'Hall of Water'), (6, b'Hall of Wind'), (7, b'Hall of Dark'), (8, b'Hall of Light'), (9, b'Garen Forest'), (10, b'Mt. Siz'), (11, b'Kabir Ruins'), (12, b'Mt. White Ragon'), (13, b'Telain Forest'), (14, b'Hydeni Ruins'), (15, b'Tamor Desert'), (16, b'Vrofagus Ruins'), (17, b'Faimon Volcano'), (18, b'Aiden Forest'), (19, b'Ferun Castle'), (20, b'Mt. Ruinar'), (21, b'Chiruka Remains')])),
                ('stage', models.IntegerField(help_text=b'Floor for Caiross or stage for scenarios')),
                ('difficulty', models.IntegerField(blank=True, help_text=b'For scenarios only', null=True, choices=[(0, b'Normal'), (1, b'Hard'), (3, b'Hell')])),
                ('success', models.BooleanField()),
                ('clear_time', models.DurationField()),
                ('mana', models.IntegerField()),
                ('crystal', models.IntegerField()),
                ('drop_type', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (100, b'Monster'), (101, b'Rune'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence')])),
                ('drop_quantity', models.IntegerField()),
                ('drop_monster', models.ForeignKey(blank=True, to='sw_parser.MonsterDrop', null=True)),
                ('drop_rune', models.ForeignKey(blank=True, to='sw_parser.RuneDrop', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SummonLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField()),
                ('server', models.IntegerField(choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia')])),
                ('summon_method', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)')])),
                ('monster', models.ForeignKey(to='sw_parser.MonsterDrop')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
