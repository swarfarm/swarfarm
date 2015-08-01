# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0028_monstersource_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monstersource',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
