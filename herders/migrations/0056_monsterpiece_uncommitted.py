# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0055_auto_20160122_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterpiece',
            name='uncommitted',
            field=models.BooleanField(default=False),
        ),
    ]
