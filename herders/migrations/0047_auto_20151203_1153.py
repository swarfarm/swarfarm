# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0046_auto_20151126_0907'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='max_lvl_attack',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='max_lvl_defense',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='max_lvl_hp',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
