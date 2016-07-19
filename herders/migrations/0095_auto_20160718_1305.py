# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0094_auto_20160615_1346'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monsterskillscalingstat',
            options={'ordering': ['stat']},
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='has_substat_upgrades',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='max_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='main_stat_value',
            field=models.IntegerField(),
        ),
    ]
