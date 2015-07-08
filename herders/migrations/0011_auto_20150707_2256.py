# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0010_auto_20150707_2215'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monster',
            old_name='base_HP',
            new_name='base_hp',
        ),
    ]
