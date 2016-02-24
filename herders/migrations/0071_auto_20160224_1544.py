# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0070_monsterskill_aoe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterskill',
            name='hits',
            field=models.IntegerField(default=1, null=True, blank=True),
        ),
    ]
