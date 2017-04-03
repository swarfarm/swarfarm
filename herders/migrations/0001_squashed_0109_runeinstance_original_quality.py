# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import colorfield.fields
import django.contrib.postgres.fields
from django.conf import settings
import timezone_field.fields
import uuid


class Migration(migrations.Migration):

    replaces = [(b'herders', '0001_initial'), (b'herders', '0002_team_leader'), (b'herders', '0003_auto_20150705_0103'), (b'herders', '0004_auto_20150706_1344'), (b'herders', '0005_auto_20150706_1421'), (b'herders', '0006_monsterskill_slot'), (b'herders', '0007_monsterskill_passive'), (b'herders', '0008_auto_20150706_1931'), (b'herders', '0009_auto_20150707_2156'), (b'herders', '0010_auto_20150707_2215'), (b'herders', '0011_auto_20150707_2256'), (b'herders', '0012_auto_20150708_2254'), (b'herders', '0013_monsterinstance_ignore_for_fusion'), (b'herders', '0014_auto_20150713_2151'), (b'herders', '0015_auto_20150714_2114'), (b'herders', '0016_auto_20150714_2129'), (b'herders', '0017_auto_20150714_2359'), (b'herders', '0018_auto_20150724_1637'), (b'herders', '0019_event'), (b'herders', '0020_auto_20150724_1647'), (b'herders', '0021_auto_20150724_1650'), (b'herders', '0022_auto_20150724_1653'), (b'herders', '0023_gameevent_day_of_week'), (b'herders', '0024_gameevent_all_day'), (b'herders', '0025_auto_20150724_1701'), (b'herders', '0026_auto_20150727_1349'), (b'herders', '0027_auto_20150731_1635'), (b'herders', '0028_monstersource_description'), (b'herders', '0029_auto_20150731_1714'), (b'herders', '0030_auto_20150804_1206'), (b'herders', '0031_auto_20150805_1308'), (b'herders', '0032_auto_20150805_1312'), (b'herders', '0033_auto_20150817_2141'), (b'herders', '0034_summoner_following'), (b'herders', '0035_monster_summonerswar_co_url'), (b'herders', '0036_monster_wikia_url'), (b'herders', '0037_auto_20150924_1720'), (b'herders', '0038_auto_20150925_1327'), (b'herders', '0039_auto_20150925_1400'), (b'herders', '0040_monster_bestiary_slug'), (b'herders', '0041_runeinstance_quality'), (b'herders', '0042_auto_20151014_1341'), (b'herders', '0043_auto_20151117_1216'), (b'herders', '0044_auto_20151117_1839'), (b'herders', '0045_auto_20151125_2146'), (b'herders', '0046_auto_20151126_0907'), (b'herders', '0047_auto_20151203_1153'), (b'herders', '0048_auto_20151208_0947'), (b'herders', '0049_auto_20151209_2159'), (b'herders', '0050_auto_20151210_2004'), (b'herders', '0051_auto_20151215_1342'), (b'herders', '0052_monsterskill_cooltime'), (b'herders', '0053_auto_20160105_2025'), (b'herders', '0054_auto_20160118_1623'), (b'herders', '0055_auto_20160122_1253'), (b'herders', '0056_monsterpiece_uncommitted'), (b'herders', '0057_auto_20160129_0948'), (b'herders', '0058_auto_20160201_2021'), (b'herders', '0059_monsterskilleffectdetail_random'), (b'herders', '0060_runeinstance_efficiency'), (b'herders', '0061_auto_20160209_2121'), (b'herders', '0062_auto_20160215_1352'), (b'herders', '0063_monsterskilleffectdetail_on_crit'), (b'herders', '0064_auto_20160217_2107'), (b'herders', '0065_auto_20160222_1951'), (b'herders', '0066_auto_20160222_2025'), (b'herders', '0067_monsterskillscaleswith_add_to_atk'), (b'herders', '0068_auto_20160224_0929'), (b'herders', '0069_monsterskilleffectdetail_damage'), (b'herders', '0070_monsterskill_aoe'), (b'herders', '0071_auto_20160224_1544'), (b'herders', '0072_auto_20160322_1549'), (b'herders', '0073_auto_20160322_1601'), (b'herders', '0074_remove_monstertag_image'), (b'herders', '0075_auto_20160323_2109'), (b'herders', '0076_auto_20160323_2111'), (b'herders', '0077_auto_20160325_1144'), (b'herders', '0078_runecraftinstance'), (b'herders', '0079_auto_20160407_1956'), (b'herders', '0080_auto_20160409_1945'), (b'herders', '0081_auto_20160420_1551'), (b'herders', '0082_auto_20160426_2021'), (b'herders', '0083_auto_20160426_2033'), (b'herders', '0084_building_buildinginstance'), (b'herders', '0085_building_icon_filename'), (b'herders', '0086_building_name'), (b'herders', '0087_buildinginstance_building'), (b'herders', '0088_auto_20160513_1644'), (b'herders', '0089_auto_20160517_1459'), (b'herders', '0090_runeinstance_notes'), (b'herders', '0091_auto_20160606_1914'), (b'herders', '0092_auto_20160608_2153'), (b'herders', '0093_auto_20160612_2201'), (b'herders', '0094_auto_20160615_1346'), (b'herders', '0095_auto_20160718_1305'), (b'herders', '0096_auto_20160718_2220'), (b'herders', '0097_auto_20160815_1900'), (b'herders', '0098_monsterinstance_avg_rune_efficiency'), (b'herders', '0099_auto_20160908_1248'), (b'herders', '0100_storage'), (b'herders', '0101_auto_20160916_1634'), (b'herders', '0102_auto_20160916_1651'), (b'herders', '0103_auto_20160920_1110'), (b'herders', '0104_auto_20160920_1111'), (b'herders', '0105_monster_summonerswarmonsters_url'), (b'herders', '0106_auto_20170130_2017'), (b'herders', '0107_auto_20170221_1245'), (b'herders', '0108_remove_storage_uncommitted'), (b'herders', '0109_runeinstance_original_quality')]

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
                ('level_progress_description', models.TextField(null=True, blank=True)),
                ('icon_filename', models.CharField(max_length=100, null=True, blank=True)),
                ('skill_effect', models.ManyToManyField(to=b'herders.MonsterSkillEffect', blank=True)),
                ('general_leader', models.BooleanField(default=False)),
                ('slot', models.IntegerField(default=1)),
                ('passive', models.BooleanField(default=False)),
            ],
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
            field=models.ManyToManyField(to=b'herders.MonsterInstance'),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner'),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner'),
        ),
        migrations.AddField(
            model_name='monster',
            name='skills',
            field=models.ManyToManyField(to=b'herders.MonsterSkill', blank=True),
        ),
        migrations.AddField(
            model_name='fusion',
            name='ingredients',
            field=models.ManyToManyField(to=b'herders.Monster'),
        ),
        migrations.AddField(
            model_name='fusion',
            name='product',
            field=models.ForeignKey(related_name='product', to='herders.Monster'),
        ),
        migrations.AddField(
            model_name='team',
            name='leader',
            field=models.ForeignKey(related_name='team_leader', blank=True, to='herders.MonsterInstance', null=True),
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
            field=models.ManyToManyField(to=b'herders.MonsterInstance', blank=True),
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
                ('dungeon_skill', models.BooleanField(default=False)),
                ('element_skill', models.BooleanField(default=False)),
                ('element', models.CharField(blank=True, max_length=6, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')])),
                ('arena_skill', models.BooleanField(default=False)),
                ('guild_skill', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='monsterskill',
            name='arena_leader',
        ),
        migrations.RemoveField(
            model_name='monsterskill',
            name='dungeon_leader',
        ),
        migrations.RemoveField(
            model_name='monsterskill',
            name='general_leader',
        ),
        migrations.RemoveField(
            model_name='monsterskill',
            name='guild_leader',
        ),
        migrations.AddField(
            model_name='monster',
            name='leader_skill',
            field=models.ForeignKey(blank=True, to='herders.MonsterLeaderSkill', null=True),
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
                ('timezone', timezone_field.fields.TimeZoneField(default=b'America/Los_Angeles')),
                ('end_date', models.DateField(null=True, blank=True)),
                ('start_date', models.DateField(null=True, blank=True)),
                ('day_of_week', models.IntegerField(blank=True, null=True, choices=[(6, b'Sunday'), (0, b'Monday'), (1, b'Tuesday'), (2, b'Wednesday'), (3, b'Thursday'), (4, b'Friday'), (5, b'Saturday')])),
                ('all_day', models.BooleanField(default=False)),
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
            field=models.ManyToManyField(to=b'herders.MonsterSource', blank=True),
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
            field=models.ManyToManyField(related_name='followed_by', to=b'herders.Summoner'),
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
        migrations.RemoveField(
            model_name='runeinstance',
            name='monster',
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='assigned_to',
            field=models.ForeignKey(blank=True, to='herders.MonsterInstance', null=True),
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
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='arena_skill',
        ),
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='dungeon_skill',
        ),
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='element_skill',
        ),
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='guild_skill',
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
            field=models.ForeignKey(related_name='content_type_awaken_bonus', blank=True, to='contenttypes.ContentType', null=True),
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
            name='awaken_ele_mats_high',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_low',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_mid',
            field=models.IntegerField(default=0),
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
        migrations.AddField(
            model_name='monsterskill',
            name='atk_multiplier',
            field=models.IntegerField(null=True, blank=True),
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
            name='scales_with',
            field=models.ManyToManyField(to=b'herders.MonsterSkillScalingStat', through='herders.MonsterSkillScalesWith'),
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
                ('monster', models.ForeignKey(to='herders.Monster')),
                ('owner', models.ForeignKey(to='herders.Summoner')),
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
                ('effect', models.ForeignKey(to='herders.MonsterSkillEffect')),
                ('skill', models.ForeignKey(to='herders.MonsterSkill')),
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
            field=models.ManyToManyField(related_name='effect', through='herders.MonsterSkillEffectDetail', to=b'herders.MonsterSkillEffect', blank=True),
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
        migrations.RemoveField(
            model_name='monster',
            name='awaken_ele_mats_high',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='awaken_ele_mats_low',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='awaken_ele_mats_mid',
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
                ('color', colorfield.fields.ColorField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='tags',
            field=models.ManyToManyField(to=b'herders.MonsterTag', blank=True),
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
                ('owner', models.ForeignKey(to='herders.Summoner')),
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
        migrations.RemoveField(
            model_name='summoner',
            name='global_server',
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
                ('owner', models.ForeignKey(to='herders.Summoner')),
                ('building', models.ForeignKey(default=0, to='herders.Building')),
            ],
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.RemoveField(
            model_name='monsterskill',
            name='atk_multiplier',
        ),
        migrations.RemoveField(
            model_name='monsterskill',
            name='scales_with',
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='multiplier_formula',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='scaling_stats',
            field=models.ManyToManyField(to=b'herders.MonsterSkillScalingStat', blank=True),
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
                ('owner', models.OneToOneField(to='herders.Summoner')),
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
                ('source', models.ManyToManyField(to=b'herders.MonsterSource', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='HomunculusSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mana_cost', models.IntegerField(default=0)),
                ('materials', models.ManyToManyField(to=b'herders.CraftCost', blank=True)),
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
            field=models.ManyToManyField(to=b'herders.Monster'),
        ),
        migrations.AddField(
            model_name='homunculusskill',
            name='prerequisites',
            field=models.ManyToManyField(related_name='homunculus_prereq', to=b'herders.MonsterSkill', blank=True),
        ),
        migrations.AddField(
            model_name='homunculusskill',
            name='skill',
            field=models.ForeignKey(to='herders.MonsterSkill'),
        ),
        migrations.CreateModel(
            name='HomunculusSkillCraftCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('craft', models.ForeignKey(to='herders.CraftMaterial')),
            ],
        ),
        migrations.CreateModel(
            name='MonsterCraftCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
                ('craft', models.ForeignKey(to='herders.CraftMaterial')),
                ('monster', models.ForeignKey(to='herders.Monster')),
            ],
        ),
        migrations.RemoveField(
            model_name='homunculusskill',
            name='materials',
        ),
        migrations.DeleteModel(
            name='CraftCost',
        ),
        migrations.AddField(
            model_name='homunculusskillcraftcost',
            name='skill',
            field=models.ForeignKey(to='herders.HomunculusSkill'),
        ),
        migrations.AddField(
            model_name='homunculusskill',
            name='craft_materials',
            field=models.ManyToManyField(to=b'herders.CraftMaterial', through='herders.HomunculusSkillCraftCost'),
        ),
        migrations.AddField(
            model_name='monster',
            name='craft_materials',
            field=models.ManyToManyField(to=b'herders.CraftMaterial', through='herders.MonsterCraftCost'),
        ),
        migrations.AddField(
            model_name='monster',
            name='summonerswarmonsters_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_dark_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_dark_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_dark_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_fire_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_fire_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_fire_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_light_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_light_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_light_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_magic_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_magic_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_magic_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_water_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_water_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_water_mid',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_wind_high',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_wind_low',
        ),
        migrations.RemoveField(
            model_name='summoner',
            name='storage_wind_mid',
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='original_quality',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
    ]
