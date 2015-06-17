# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0028_auto_20150617_1259'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='image_filename',
            field=models.CharField(max_length=250, null=True, blank=True),
        ),
    ]
