# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0100_storage'),
    ]

    operations = [
        migrations.CreateModel(
            name='CraftCost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='CraftMaterials',
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
                ('materials', models.ManyToManyField(to='herders.CraftCost', blank=True)),
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
            model_name='monster',
            name='skill_reset_crystals',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='storage',
            name='cloth',
            field=models.IntegerField(default=0, help_text=b'Thick Cloth'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='crystal_dark',
            field=models.IntegerField(default=0, help_text=b'Pitch-black Dark Crystal'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='crystal_fire',
            field=models.IntegerField(default=0, help_text=b'Flaming Fire Crystal'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='crystal_light',
            field=models.IntegerField(default=0, help_text=b'Shiny Light Crystal'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='crystal_magic',
            field=models.IntegerField(default=0, help_text=b'Condensed Magic Crystal'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='crystal_pure',
            field=models.IntegerField(default=0, help_text=b'Pure Magic Crystal'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='crystal_water',
            field=models.IntegerField(default=0, help_text=b'Frozen Water Crystal'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='crystal_wind',
            field=models.IntegerField(default=0, help_text=b'Whirling Wind Crystal'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='dark_essence',
            field=django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Dark Essence', base_field=models.IntegerField(default=0), size=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='dust',
            field=models.IntegerField(default=0, help_text=b'Magic Dust'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='fire_essence',
            field=django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Fire Essence', base_field=models.IntegerField(default=0), size=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='leather',
            field=models.IntegerField(default=0, help_text=b'Tough Leather'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='light_essence',
            field=django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Light Essence', base_field=models.IntegerField(default=0), size=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='magic_essence',
            field=django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Magic Essence', base_field=models.IntegerField(default=0), size=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='mithril',
            field=models.IntegerField(default=0, help_text=b'Shining Mythril'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='ore',
            field=models.IntegerField(default=0, help_text=b'Solid Iron Ore'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='rock',
            field=models.IntegerField(default=0, help_text=b'Solid Rock'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='rune_piece',
            field=models.IntegerField(default=0, help_text=b'Rune Piece'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='symbol_chaos',
            field=models.IntegerField(default=0, help_text=b'Symbol of Chaos'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='symbol_harmony',
            field=models.IntegerField(default=0, help_text=b'Symbol of Harmony'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='symbol_transcendance',
            field=models.IntegerField(default=0, help_text=b'Symbol of Transcendance'),
        ),
        migrations.AlterField(
            model_name='storage',
            name='water_essence',
            field=django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Water Essence', base_field=models.IntegerField(default=0), size=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='wind_essence',
            field=django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], help_text=b'Wind Essence', base_field=models.IntegerField(default=0), size=3),
        ),
        migrations.AlterField(
            model_name='storage',
            name='wood',
            field=models.IntegerField(default=0, help_text=b'Hard Wood'),
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
            field=models.ForeignKey(to='herders.MonsterSkill'),
        ),
        migrations.AddField(
            model_name='craftcost',
            name='craft',
            field=models.ForeignKey(to='herders.CraftMaterials'),
        ),
        migrations.AddField(
            model_name='monster',
            name='craft_materials',
            field=models.ManyToManyField(to='herders.CraftCost', blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='skill_reset_craft_materials',
            field=models.ManyToManyField(related_name='skill_reset_craft_materials', to='herders.CraftCost', blank=True),
        ),
    ]
