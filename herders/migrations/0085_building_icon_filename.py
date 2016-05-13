# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0084_building_buildinginstance'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='icon_filename',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
