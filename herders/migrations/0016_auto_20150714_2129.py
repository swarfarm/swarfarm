# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0015_auto_20150714_2114'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterleaderskill',
            name='element',
            field=models.CharField(blank=True, max_length=6, null=True, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')]),
        ),
    ]
