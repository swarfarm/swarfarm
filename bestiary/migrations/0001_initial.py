# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0001_squashed_0003_remove_monstertag_color'),
    ]

    operations = [
        migrations.CreateModel(
            name='Effect',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monsterskilleffect',),
        ),
        migrations.CreateModel(
            name='EffectDetail',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monsterskilleffectdetail',),
        ),
        migrations.CreateModel(
            name='Fusion',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.fusion',),
        ),
        migrations.CreateModel(
            name='LeaderSkill',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monsterleaderskill',),
        ),
        migrations.CreateModel(
            name='Monster',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monster',),
        ),
        migrations.CreateModel(
            name='ScalesWith',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monsterskillscaleswith',),
        ),
        migrations.CreateModel(
            name='ScalingStat',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monsterskillscalingstat',),
        ),
        migrations.CreateModel(
            name='Skill',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monsterskill',),
        ),
        migrations.CreateModel(
            name='Source',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.monstersource',),
        ),
    ]
