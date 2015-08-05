# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0031_auto_20150805_1308'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fusion',
            name='meta_order',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AlterField(
            model_name='monstersource',
            name='meta_order',
            field=models.IntegerField(default=0, db_index=True),
        ),
    ]
