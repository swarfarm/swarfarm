# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0093_auto_20160612_2201'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterskill',
            name='multiplier_formula',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterskill',
            name='multiplier_formula_raw',
            field=models.CharField(max_length=150, null=True, blank=True),
        ),
    ]
