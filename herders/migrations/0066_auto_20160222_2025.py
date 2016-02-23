# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0065_auto_20160222_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterskillscaleswith',
            name='multiplier',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
