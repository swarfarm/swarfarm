# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0083_auto_20160426_2033'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('com2us_id', models.IntegerField()),
                ('max_level', models.IntegerField()),
                ('area', models.IntegerField(choices=[(0, b'Everywhere'), (1, b'Guild Battle')])),
                ('affected_stat', models.IntegerField(choices=[(0, b'HP'), (1, b'ATK'), (2, b'DEF'), (3, b'SPD'), (4, b'CRI Rate %'), (5, b'CRI Dmg %'), (6, b'Resistance %'), (7, b'Accuracy %')])),
                ('element', models.CharField(blank=True, max_length=6, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')])),
                ('stat_bonus', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None)),
                ('upgrade_cost', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None)),
            ],
        ),
        migrations.CreateModel(
            name='BuildingInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('level', models.IntegerField()),
                ('owner', models.ForeignKey(to='herders.Summoner')),
            ],
        ),
    ]
