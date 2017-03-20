# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0108_remove_storage_uncommitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='original_quality',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
    ]
