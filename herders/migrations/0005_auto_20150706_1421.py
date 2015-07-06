# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0004_auto_20150706_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterskill',
            name='icon_filename',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterskilleffect',
            name='icon_filename',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
