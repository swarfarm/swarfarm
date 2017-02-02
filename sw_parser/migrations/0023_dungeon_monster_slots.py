# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0022_auto_20170106_1315'),
    ]

    operations = [
        migrations.AddField(
            model_name='dungeon',
            name='monster_slots',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None), blank=True),
        ),
    ]
