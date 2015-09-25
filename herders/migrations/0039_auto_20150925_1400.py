# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0038_auto_20150925_1327'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='has_accuracy',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_atk',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_crit_dmg',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_crit_rate',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_def',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_hp',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_resist',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_speed',
            field=models.BooleanField(default=False),
        ),
    ]
