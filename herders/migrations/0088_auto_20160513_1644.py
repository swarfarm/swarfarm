# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0087_buildinginstance_building'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='building',
            name='affected_stat',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'HP'), (1, b'ATK'), (2, b'DEF'), (3, b'SPD'), (4, b'CRI Rate %'), (5, b'CRI Dmg %'), (6, b'Resistance %'), (7, b'Accuracy %')]),
        ),
        migrations.AlterField(
            model_name='building',
            name='area',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Everywhere'), (1, b'Guild Battle')]),
        ),
    ]
