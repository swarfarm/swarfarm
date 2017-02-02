# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0009_auto_20160508_1133'),
    ]

    operations = [
        migrations.AddField(
            model_name='runedrop',
            name='quality',
            field=models.IntegerField(default=0, choices=[(0, b'Normal'), (1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
        migrations.AlterField(
            model_name='dungeon',
            name='type',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Scenario'), (1, b'Rune Dungeon'), (2, b'Essence Dungeon'), (3, b'Other Dungeon'), (4, b'Raid'), (5, b'Hall of Heroes')]),
        ),
    ]
