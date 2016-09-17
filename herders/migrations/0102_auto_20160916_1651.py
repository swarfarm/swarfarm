# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0101_auto_20160916_1634'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='CraftMaterials',
            new_name='CraftMaterial',
        ),
    ]
