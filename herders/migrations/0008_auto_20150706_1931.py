# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0007_monsterskill_passive'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterskill',
            name='level_progress_description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterskill',
            name='skill_effect',
            field=models.ManyToManyField(to='herders.MonsterSkillEffect', blank=True),
        ),
    ]
