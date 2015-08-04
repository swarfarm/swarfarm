# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0029_auto_20150731_1714'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monstersource',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='monster',
            name='obtainable',
            field=models.BooleanField(default=True),
        ),
    ]
