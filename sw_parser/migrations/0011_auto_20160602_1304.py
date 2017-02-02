# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0010_auto_20160517_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='dungeon',
            name='energy_cost',
            field=django.contrib.postgres.fields.ArrayField(size=None, null=True, base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(null=True, blank=True), size=None), blank=True),
        ),
        migrations.AlterField(
            model_name='runlog',
            name='difficulty',
            field=models.IntegerField(blank=True, help_text=b'For scenarios only', null=True, choices=[(0, b'Normal'), (1, b'Hard'), (2, b'Hell')]),
        ),
    ]
