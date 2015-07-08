# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0008_auto_20150706_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='base_HP',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_accuracy',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_attack',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_crit_damage',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_crit_rate',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_defense',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_resistance',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='base_speed',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
