# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0075_auto_20160323_2109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterinstance',
            name='priority',
            field=models.IntegerField(blank=True, null=True, choices=[(1, b'Low'), (2, b'Medium'), (3, b'High')]),
        ),
    ]
