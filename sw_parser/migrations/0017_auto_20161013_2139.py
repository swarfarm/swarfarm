# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0104_auto_20160920_1111'),
        ('sw_parser', '0016_auto_20161010_2230'),
    ]

    operations = [
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
                ('log', models.ForeignKey(to='sw_parser.RiftDungeonLog')),
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
            field=models.ForeignKey(to='sw_parser.RiftDungeonLog'),
        ),
    ]
