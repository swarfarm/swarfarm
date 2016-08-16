# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0096_auto_20160718_2220'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='substat_crafts',
            field=django.contrib.postgres.fields.ArrayField(size=4, null=True, base_field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]), blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_values',
            field=django.contrib.postgres.fields.ArrayField(size=4, null=True, base_field=models.IntegerField(null=True, blank=True), blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substats',
            field=django.contrib.postgres.fields.ArrayField(size=4, null=True, base_field=models.IntegerField(blank=True, null=True, choices=[(1, b'HP'), (2, b'HP %'), (3, b'ATK'), (4, b'ATK %'), (5, b'DEF'), (6, b'DEF %'), (7, b'SPD'), (8, b'CRI Rate %'), (9, b'CRI Dmg %'), (10, b'Resistance %'), (11, b'Accuracy %')]), blank=True),
        ),
    ]
