# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0027_auto_20150731_1635'),
    ]

    operations = [
        migrations.AddField(
            model_name='monstersource',
            name='description',
            field=models.TextField(null=True),
        ),
    ]
