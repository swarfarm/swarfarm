# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0091_auto_20160606_1914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monsterskillscaleswith',
            name='monsterskill',
        ),
        migrations.RemoveField(
            model_name='monsterskillscaleswith',
            name='scalingstat',
        ),
        migrations.AddField(
            model_name='monsterskillscalingstat',
            name='com2us_desc',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterskill',
            name='scaling_stats',
            field=models.ManyToManyField(to='herders.MonsterSkillScalingStat', blank=True),
        ),
        migrations.AlterField(
            model_name='runecraftinstance',
            name='quality',
            field=models.IntegerField(choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
        migrations.DeleteModel(
            name='MonsterSkillScalesWith',
        ),
    ]
