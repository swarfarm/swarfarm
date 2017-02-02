# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0026_exportmanager'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exportmanager',
            old_name='model_name',
            new_name='export_category',
        ),
        migrations.RemoveField(
            model_name='exportmanager',
            name='timestamp',
        ),
        migrations.AlterField(
            model_name='exportmanager',
            name='last_row',
            field=models.BigIntegerField(default=0),
        ),
    ]
