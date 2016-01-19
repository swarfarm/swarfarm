# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0053_auto_20160105_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterinstance',
            name='uncommitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='uncommitted',
            field=models.BooleanField(default=False),
        ),
    ]
