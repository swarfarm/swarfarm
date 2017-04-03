# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    replaces = [(b'sw_parser', '0001_squashed_0004_auto_20160420_2220'), (b'sw_parser', '0002_auto_20160421_0957'), (b'sw_parser', '0003_auto_20160421_2028'), (b'sw_parser', '0004_auto_20160421_2113'), (b'sw_parser', '0005_auto_20160426_1632'), (b'sw_parser', '0003_auto_20160422_0914'), (b'sw_parser', '0006_merge'), (b'sw_parser', '0007_auto_20160502_0911'), (b'sw_parser', '0008_runlog_energy'), (b'sw_parser', '0009_auto_20160508_1133'), (b'sw_parser', '0010_auto_20160517_1459'), (b'sw_parser', '0011_auto_20160602_1304'), (b'sw_parser', '0012_dungeon_slug'), (b'sw_parser', '0013_auto_20160916_1517'), (b'sw_parser', '0014_auto_20161010_2200'), (b'sw_parser', '0015_auto_20161010_2223'), (b'sw_parser', '0016_auto_20161010_2230'), (b'sw_parser', '0017_auto_20161013_2139'), (b'sw_parser', '0018_auto_20161017_2040'), (b'sw_parser', '0019_auto_20161020_1317'), (b'sw_parser', '0020_auto_20161221_1016'), (b'sw_parser', '0021_auto_20161221_2235'), (b'sw_parser', '0022_auto_20170106_1315'), (b'sw_parser', '0023_dungeon_monster_slots'), (b'sw_parser', '0024_shoprefreshlog_slots_available'), (b'sw_parser', '0025_remove_worldbosslog_worldboss'), (b'sw_parser', '0026_exportmanager'), (b'sw_parser', '0027_auto_20170127_1112'), (b'sw_parser', '0028_auto_20170131_1149'), (b'sw_parser', '0029_auto_20170131_1339'), (b'sw_parser', '0030_auto_20170207_1738'), (b'sw_parser', '0031_auto_20170208_1201'), (b'sw_parser', '0032_auto_20170209_0732'), (b'sw_parser', '0033_auto_20170214_1051')]

    dependencies = [
        ('herders', '0001_squashed_0109_runeinstance_original_quality'),
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
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('dungeon', models.ForeignKey(to='sw_parser.Dungeon')),
                ('stage', models.IntegerField(help_text=b'Floor for Caiross or stage for scenarios', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)])),
                ('difficulty', models.IntegerField(blank=True, help_text=b'For scenarios only', null=True, choices=[(0, b'Normal'), (1, b'Hard'), (2, b'Hell')])),
                ('success', models.NullBooleanField()),
                ('clear_time', models.DurationField(null=True, blank=True)),
                ('mana', models.IntegerField(null=True, blank=True)),
                ('crystal', models.IntegerField(null=True, blank=True)),
                ('drop_type', models.IntegerField(blank=True, null=True, choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (100, b'Monster'), (101, b'Rune'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (154, b'Event Item')])),
                ('drop_quantity', models.IntegerField(null=True, blank=True)),
                ('drop_monster', models.ForeignKey(blank=True, to='sw_parser.MonsterDrop', null=True)),
                ('drop_rune', models.ForeignKey(blank=True, to='sw_parser.RuneDrop', null=True)),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
                ('energy', models.IntegerField(null=True, blank=True)),
                ('battle_key', models.BigIntegerField(db_index=True, null=True, blank=True)),
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
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('summon_method', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll')])),
                ('monster', models.ForeignKey(to='sw_parser.MonsterDrop')),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Dungeon',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterModelOptions(
            name='dungeon',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='dungeon',
            name='type',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Scenario'), (1, b'Rune Dungeon'), (2, b'Essence Dungeon'), (3, b'Other Dungeon'), (4, b'Raid')]),
        ),
        migrations.AddField(
            model_name='dungeon',
            name='max_floors',
            field=models.IntegerField(default=10),
        ),
        migrations.AlterModelOptions(
            name='dungeon',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='runedrop',
            name='quality',
            field=models.IntegerField(default=0, choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
        migrations.AlterField(
            model_name='dungeon',
            name='type',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Scenario'), (1, b'Rune Dungeon'), (2, b'Essence Dungeon'), (3, b'Other Dungeon'), (4, b'Raid'), (5, b'Hall of Heroes')]),
        ),
        migrations.AddField(
            model_name='dungeon',
            name='energy_cost',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None), blank=True),
        ),
        migrations.AddField(
            model_name='dungeon',
            name='slug',
            field=models.SlugField(null=True, blank=True),
        ),
        migrations.CreateModel(
            name='RiftDungeonItemDrop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal')])),
                ('quantity', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RiftDungeonLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('dungeon', models.IntegerField(choices=[(1001, b'Ice Beast'), (2001, b'Fire Beast'), (3001, b'Wind Beast'), (4001, b'Light Beast'), (5001, b'Dark Beast')])),
                ('grade', models.IntegerField(choices=[(1, b'F'), (2, b'D'), (3, b'C'), (4, b'B-'), (5, b'B'), (6, b'B+'), (7, b'A-'), (8, b'A'), (9, b'A+'), (10, b'S'), (11, b'SS'), (12, b'SSS')])),
                ('total_damage', models.IntegerField()),
                ('success', models.BooleanField()),
                ('mana', models.IntegerField(default=0)),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RiftDungeonMonsterDrop',
            fields=[
                ('monsterdrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.MonsterDrop')),
                ('log', models.ForeignKey(related_name='monster_drops', to='sw_parser.RiftDungeonLog')),
            ],
            bases=('sw_parser.monsterdrop',),
        ),
        migrations.AlterField(
            model_name='dungeon',
            name='type',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Scenarios'), (1, b'Rune Dungeons'), (2, b'Elemental Dungeons'), (3, b'Other Dungeons'), (4, b'Raids'), (5, b'Hall of Heroes')]),
        ),
        migrations.AddField(
            model_name='riftdungeonitemdrop',
            name='log',
            field=models.ForeignKey(related_name='item_drops', to='sw_parser.RiftDungeonLog'),
        ),
        migrations.CreateModel(
            name='RuneCraft',
            fields=[
                ('runedrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.RuneDrop')),
            ],
            bases=('sw_parser.runedrop',),
        ),
        migrations.CreateModel(
            name='RuneCraftLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('craft_level', models.IntegerField(choices=[(0, b'Low'), (1, b'Mid'), (2, b'High')])),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='runecraft',
            name='log',
            field=models.ForeignKey(related_name='rune', to='sw_parser.RuneCraftLog'),
        ),
        migrations.CreateModel(
            name='ShopRefreshItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal')])),
                ('quantity', models.IntegerField()),
                ('cost', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShopRefreshLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShopRefreshMonster',
            fields=[
                ('monsterdrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.MonsterDrop')),
                ('cost', models.IntegerField()),
                ('log', models.ForeignKey(related_name='monster_drops', to='sw_parser.ShopRefreshLog')),
            ],
            bases=('sw_parser.monsterdrop',),
        ),
        migrations.CreateModel(
            name='ShopRefreshRune',
            fields=[
                ('runedrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.RuneDrop')),
                ('cost', models.IntegerField()),
                ('log', models.ForeignKey(related_name='rune_drops', to='sw_parser.ShopRefreshLog')),
            ],
            bases=('sw_parser.runedrop',),
        ),
        migrations.AlterField(
            model_name='riftdungeonitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal')]),
        ),
        migrations.AddField(
            model_name='shoprefreshitem',
            name='log',
            field=models.ForeignKey(related_name='item_drops', to='sw_parser.ShopRefreshLog'),
        ),
        migrations.CreateModel(
            name='WorldBossItemDrop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money')])),
                ('quantity', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorldBossLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('worldboss', models.IntegerField(choices=[(10051, b"Primal Giant Pan'ghor")])),
                ('grade', models.IntegerField(choices=[(1, b'F'), (2, b'D'), (3, b'C'), (4, b'B-'), (5, b'B'), (6, b'B+'), (7, b'A-'), (8, b'A'), (9, b'A+'), (10, b'S'), (11, b'SS'), (12, b'SSS')])),
                ('damage', models.IntegerField()),
                ('battle_points', models.IntegerField()),
                ('bonus_battle_points', models.IntegerField()),
                ('avg_monster_level', models.FloatField()),
                ('monster_count', models.IntegerField()),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WorldBossMonsterDrop',
            fields=[
                ('monsterdrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.MonsterDrop')),
                ('log', models.ForeignKey(related_name='monster_drops', to='sw_parser.WorldBossLog')),
            ],
            bases=('sw_parser.monsterdrop',),
        ),
        migrations.CreateModel(
            name='WorldBossRuneDrop',
            fields=[
                ('runedrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.RuneDrop')),
                ('log', models.ForeignKey(related_name='rune_drops', to='sw_parser.WorldBossLog')),
            ],
            bases=('sw_parser.runedrop',),
        ),
        migrations.AlterField(
            model_name='riftdungeonitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money')]),
        ),
        migrations.AlterField(
            model_name='shoprefreshitem',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money')]),
        ),
        migrations.AddField(
            model_name='worldbossitemdrop',
            name='log',
            field=models.ForeignKey(related_name='item_drops', to='sw_parser.WorldBossLog'),
        ),
        migrations.AddField(
            model_name='worldbosslog',
            name='battle_key',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='riftdungeonitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money')]),
        ),
        migrations.AlterField(
            model_name='shoprefreshitem',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money')]),
        ),
        migrations.AlterField(
            model_name='worldbossitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money')]),
        ),
        migrations.AddField(
            model_name='dungeon',
            name='xp',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='runedrop',
            name='type',
            field=models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy'), (17, b'Fight'), (18, b'Determination'), (19, b'Enhance'), (20, b'Accuracy'), (21, b'Tolerance')]),
        ),
        migrations.AddField(
            model_name='dungeon',
            name='monster_slots',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None), blank=True),
        ),
        migrations.AddField(
            model_name='shoprefreshlog',
            name='slots_available',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.RemoveField(
            model_name='worldbosslog',
            name='worldboss',
        ),
        migrations.CreateModel(
            name='ExportManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('export_category', models.TextField()),
                ('last_row', models.BigIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='RiftRaidItemDrop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money')])),
                ('quantity', models.IntegerField()),
                ('wizard_id', models.BigIntegerField()),
                ('battle_key', models.BigIntegerField(db_index=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RiftRaidLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('battle_key', models.BigIntegerField(db_index=True, null=True, blank=True)),
                ('raid', models.IntegerField()),
                ('action_item', models.IntegerField()),
                ('success', models.NullBooleanField()),
                ('difficulty', models.IntegerField(choices=[(1, b'R1'), (2, b'R2'), (3, b'R3'), (4, b'R4'), (5, b'R5')])),
                ('contribution', models.IntegerField(null=True, blank=True)),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RiftRaidMonsterDrop',
            fields=[
                ('monsterdrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.MonsterDrop')),
                ('wizard_id', models.BigIntegerField()),
                ('battle_key', models.BigIntegerField(db_index=True)),
                ('log', models.ForeignKey(to='sw_parser.RiftRaidLog')),
            ],
            bases=('sw_parser.monsterdrop',),
        ),
        migrations.CreateModel(
            name='RiftRaidRuneCraftDrop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.IntegerField(choices=[(0, b'Grindstone'), (1, b'Enchant Gem')])),
                ('rune', models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy'), (17, b'Fight'), (18, b'Determination'), (19, b'Enhance'), (20, b'Accuracy'), (21, b'Tolerance')])),
                ('stat', models.IntegerField(choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('quality', models.IntegerField(choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')])),
                ('value', models.IntegerField(null=True, blank=True)),
                ('wizard_id', models.BigIntegerField()),
                ('battle_key', models.BigIntegerField(db_index=True)),
                ('log', models.ForeignKey(to='sw_parser.RiftRaidLog')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='riftraiditemdrop',
            name='log',
            field=models.ForeignKey(to='sw_parser.RiftRaidLog'),
        ),
        migrations.CreateModel(
            name='WishItemDrop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('item', models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy')])),
                ('quantity', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WishLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('wish_id', models.IntegerField()),
                ('wish_sequence', models.IntegerField()),
                ('crystal_used', models.BooleanField()),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='WishMonsterDrop',
            fields=[
                ('monsterdrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.MonsterDrop')),
                ('log', models.ForeignKey(to='sw_parser.WishLog')),
            ],
            bases=('sw_parser.monsterdrop',),
        ),
        migrations.CreateModel(
            name='WishRuneDrop',
            fields=[
                ('runedrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.RuneDrop')),
                ('log', models.ForeignKey(to='sw_parser.WishLog')),
            ],
            bases=('sw_parser.runedrop',),
        ),
        migrations.AlterField(
            model_name='riftdungeonitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy')]),
        ),
        migrations.AlterField(
            model_name='riftraiditemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy')]),
        ),
        migrations.AlterField(
            model_name='shoprefreshitem',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy')]),
        ),
        migrations.AlterField(
            model_name='worldbossitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy')]),
        ),
        migrations.AddField(
            model_name='wishitemdrop',
            name='log',
            field=models.ForeignKey(to='sw_parser.WishLog'),
        ),
        migrations.AlterField(
            model_name='riftdungeonitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point')]),
        ),
        migrations.AlterField(
            model_name='riftraiditemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point')]),
        ),
        migrations.AlterField(
            model_name='shoprefreshitem',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point')]),
        ),
        migrations.AlterField(
            model_name='wishitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point')]),
        ),
        migrations.AlterField(
            model_name='worldbossitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point')]),
        ),
        migrations.AlterField(
            model_name='riftdungeonitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point'), (154, b'Event Item')]),
        ),
        migrations.AlterField(
            model_name='riftraiditemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point'), (154, b'Event Item')]),
        ),
        migrations.AlterField(
            model_name='shoprefreshitem',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point'), (154, b'Event Item')]),
        ),
        migrations.AlterField(
            model_name='wishitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point'), (154, b'Event Item')]),
        ),
        migrations.AlterField(
            model_name='worldbossitemdrop',
            name='item',
            field=models.IntegerField(choices=[(0, b'Unknown Scroll'), (1, b'Social Summon'), (2, b'Mystical Scroll'), (3, b'Mystical Summon (Crystals)'), (4, b'Fire Scroll'), (5, b'Water Scroll'), (6, b'Wind Scroll'), (7, b'Scroll of Light and Dark'), (8, b'Legendary Scroll'), (9, b'Exclusive Summon (Stones)'), (10, b'Light and Dark Pieces'), (11, b'Legendary Pieces'), (12, b'Transcendance Scroll'), (102, b'Shapeshifting Stone'), (103, b'Power Stone'), (104, b'Summoning Pieces'), (105, b'Secret Dungeon'), (110, b'Low Magic Essence'), (111, b'Mid Magic Essence'), (112, b'High Magic Essence'), (113, b'Low Fire Essence'), (114, b'Mid Fire Essence'), (115, b'High Fire Essence'), (116, b'Low Water Essence'), (117, b'Mid Water Essence'), (118, b'High Water Essence'), (119, b'Low Wind Essence'), (120, b'Mid Wind Essence'), (121, b'High Wind Essence'), (122, b'Low Light Essence'), (123, b'Mid Light Essence'), (124, b'High Light Essence'), (125, b'Low Dark Essence'), (126, b'Mid Dark Essence'), (127, b'High Dark Essence'), (128, b'Hard Wood'), (129, b'Tough Leather'), (130, b'Solid Rock'), (131, b'Solid Iron Ore'), (132, b'Shining Mithril'), (133, b'Thick Cloth'), (134, b'Rune Piece'), (135, b'Magic Dust'), (136, b'Symbol of Harmony'), (137, b'Symbol of Transcendance'), (138, b'Symbol of Chaos'), (139, b'Frozen Water Crystal'), (140, b'Flaming Fire Crystal'), (141, b'Whirling Wind Crystal'), (142, b'Shiny Light Crystal'), (143, b'Pitch-black Dark Crystal'), (144, b'Condensed Magic Crystal'), (145, b'Pure Magic Crystal'), (146, b'Mana'), (147, b'Crystals'), (148, b'Glory Points'), (149, b'Guild Points'), (150, b'Real Money'), (151, b'Energy'), (152, b'Arena Wing'), (153, b'Social Point'), (154, b'Event Item')]),
        ),
    ]
