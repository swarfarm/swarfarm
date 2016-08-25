# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0097_auto_20160815_1900'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterinstance',
            name='avg_rune_efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
