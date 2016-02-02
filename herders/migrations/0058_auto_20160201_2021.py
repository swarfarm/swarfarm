# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0057_auto_20160129_0948'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='marked_for_sale',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='value',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='summoner',
            name='com2us_id',
            field=models.BigIntegerField(default=None, null=True, blank=True),
        ),
    ]
