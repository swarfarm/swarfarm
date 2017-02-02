# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0002_auto_20160421_0957'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='dungeon',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='dungeon',
            name='type',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Scenario'), (1, b'Dungeon'), (2, b'Other')]),
        ),
    ]
