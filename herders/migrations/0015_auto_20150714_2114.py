# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0014_auto_20150713_2151'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterLeaderSkill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('attribute', models.IntegerField(choices=[(1, b'HP'), (2, b'Attack Power'), (3, b'Defense'), (4, b'Attack Speed'), (5, b'Critical Rate'), (6, b'Critical Damage'), (7, b'Resistance'), (8, b'Accuracy')])),
                ('amount', models.IntegerField()),
                ('dungeon_skill', models.BooleanField(default=False)),
                ('element_skill', models.BooleanField(default=False)),
                ('element', models.IntegerField(blank=True, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')])),
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
            name='element_leader',
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
    ]
