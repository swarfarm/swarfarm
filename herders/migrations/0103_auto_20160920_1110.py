# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0102_auto_20160916_1651'),
    ]

    operations = [
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
            ],
        ),
        migrations.RemoveField(
            model_name='craftcost',
            name='craft',
        ),
        migrations.RemoveField(
            model_name='homunculusskill',
            name='materials',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='craft_materials',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='skill_reset_craft_materials',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='skill_reset_crystals',
        ),
        migrations.DeleteModel(
            name='CraftCost',
        ),
        migrations.AddField(
            model_name='monstercraftcost',
            name='monster',
            field=models.ForeignKey(to='herders.Monster'),
        ),
        migrations.AddField(
            model_name='homunculusskillcraftcost',
            name='skill',
            field=models.ForeignKey(to='herders.HomunculusSkill'),
        ),
    ]
