# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bestiary', '0002_building'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ScalesWith',
        ),
    ]
