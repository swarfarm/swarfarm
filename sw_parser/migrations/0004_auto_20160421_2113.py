# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0003_auto_20160421_2028'),
    ]

    operations = [
        migrations.AddField(
            model_name='dungeon',
            name='max_floors',
            field=models.IntegerField(default=10),
        ),
        migrations.AlterField(
            model_name='dungeon',
            name='type',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Scenario'), (1, b'Rune Dungeon'), (2, b'Essence Dungeon'), (3, b'Other Dungeon'), (4, b'Raid')]),
        ),
        migrations.AlterField(
            model_name='runlog',
            name='stage',
            field=models.IntegerField(help_text=b'Floor for Caiross or stage for scenarios', choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)]),
        ),
    ]
