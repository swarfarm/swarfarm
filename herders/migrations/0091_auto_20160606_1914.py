# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0090_runeinstance_notes'),
    ]

    operations = [
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
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='scaling_stats',
            field=models.ManyToManyField(to='herders.MonsterSkillScalingStat'),
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
