# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0106_auto_20170130_2017'),
        ('sw_parser', '0029_auto_20170131_1339'),
    ]

    operations = [
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
    ]
