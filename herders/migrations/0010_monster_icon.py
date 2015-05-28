# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0009_auto_20150421_1958'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='icon',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
