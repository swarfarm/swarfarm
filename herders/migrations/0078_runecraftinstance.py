# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0077_auto_20160325_1144'),
    ]

    operations = [
        migrations.CreateModel(
            name='RuneCraftInstance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('com2us_id', models.BigIntegerField(null=True, blank=True)),
                ('type', models.IntegerField(choices=[(0, b'Grindstone'), (1, b'Enchant Gem')])),
                ('rune', models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy')])),
                ('stat', models.IntegerField(choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')])),
                ('quality', models.IntegerField(choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')])),
                ('value', models.IntegerField(null=True, blank=True)),
                ('uncommitted', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(to='herders.Summoner')),
            ],
        ),
    ]
