# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0021_auto_20161221_2235'),
    ]

    operations = [
        migrations.AddField(
            model_name='dungeon',
            name='xp',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='runedrop',
            name='type',
            field=models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy'), (17, b'Fight'), (18, b'Determination'), (19, b'Enhance'), (20, b'Accuracy'), (21, b'Tolerance')]),
        ),
    ]
