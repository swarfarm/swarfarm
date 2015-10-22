# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0041_runeinstance_quality'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='runeinstance',
            options={'ordering': ['type', 'slot', 'level', 'quality']},
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='quality',
            field=models.IntegerField(default=0, choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='type',
            field=models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy')]),
        ),
    ]
