# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0103_auto_20160920_1110'),
    ]

    operations = [
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
    ]
