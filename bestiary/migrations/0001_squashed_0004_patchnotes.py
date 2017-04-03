# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    replaces = [(b'bestiary', '0001_initial'), (b'bestiary', '0002_building'), (b'bestiary', '0003_delete_scaleswith'), (b'bestiary', '0004_patchnotes')]

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
        migrations.CreateModel(
            name='Building',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.building',),
        ),
        migrations.DeleteModel(
            name='ScalesWith',
        ),
        migrations.CreateModel(
            name='PatchNotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('major', models.IntegerField()),
                ('minor', models.IntegerField()),
                ('dev', models.IntegerField()),
                ('description', models.CharField(max_length=60, null=True, blank=True)),
                ('timestamp', models.DateTimeField()),
                ('detailed_notes', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
