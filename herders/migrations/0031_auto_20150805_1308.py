# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0030_auto_20150804_1206'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fusion',
            options={'ordering': ['meta_order']},
        ),
        migrations.AlterModelOptions(
            name='monstersource',
            options={'ordering': ['meta_order', 'icon_filename', 'name']},
        ),
        migrations.AddField(
            model_name='fusion',
            name='meta_order',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monstersource',
            name='meta_order',
            field=models.IntegerField(default=0),
        ),
    ]
