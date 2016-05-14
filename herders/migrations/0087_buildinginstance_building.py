# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0086_building_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='buildinginstance',
            name='building',
            field=models.ForeignKey(default=0, to='herders.Building'),
            preserve_default=False,
        ),
    ]
