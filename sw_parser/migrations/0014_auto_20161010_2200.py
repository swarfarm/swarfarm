# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0013_auto_20160916_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='runlog',
            name='battle_key',
            field=models.BigIntegerField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='runlog',
            name='success',
            field=models.NullBooleanField(),
        ),
    ]
