# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0059_monsterskilleffectdetail_random'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='efficiency',
            field=models.FloatField(null=True, blank=True),
        ),
    ]
