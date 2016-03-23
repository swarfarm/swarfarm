# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0072_auto_20160322_1549'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MonsterTags',
            new_name='MonsterTag',
        ),
    ]
