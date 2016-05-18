# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0088_auto_20160513_1644'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='affected_stat',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'HP'), (1, b'ATK'), (2, b'DEF'), (3, b'SPD'), (4, b'CRI Rate %'), (5, b'CRI Dmg %'), (6, b'Resistance %'), (7, b'Accuracy %'), (8, b'Max. Energy'), (9, b'Mana Stone Storage'), (10, b'Mana Stone Production Rate'), (11, b'Energy Production Rate'), (12, b'Arcane Tower ATK'), (13, b'Arcane Tower SPD')]),
        ),
    ]
