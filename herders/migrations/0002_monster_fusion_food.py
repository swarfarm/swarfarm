# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='fusion_food',
            field=models.BooleanField(default=False),
        ),
    ]
