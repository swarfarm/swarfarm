# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0011_auto_20150707_2256'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monster',
            old_name='base_accuracy',
            new_name='accuracy',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='base_crit_damage',
            new_name='crit_damage',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='base_crit_rate',
            new_name='crit_rate',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='base_resistance',
            new_name='resistance',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='base_speed',
            new_name='speed',
        ),
    ]
