# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0011_auto_20160602_1304'),
    ]

    operations = [
        migrations.AddField(
            model_name='dungeon',
            name='slug',
            field=models.SlugField(null=True, blank=True),
        ),
    ]
