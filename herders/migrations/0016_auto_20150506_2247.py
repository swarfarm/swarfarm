# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0015_auto_20150425_2239'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monsterinstance',
            old_name='food',
            new_name='fodder',
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='priority',
            field=models.IntegerField(default=1, choices=[(1, b'Low'), (2, b'Medium'), (3, b'High')]),
        ),
    ]
