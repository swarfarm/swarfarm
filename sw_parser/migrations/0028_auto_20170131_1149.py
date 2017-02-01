# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0027_auto_20170127_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='riftdungeonitemdrop',
            name='log',
            field=models.ForeignKey(related_name='item_drops', to='sw_parser.RiftDungeonLog'),
        ),
        migrations.AlterField(
            model_name='riftdungeonmonsterdrop',
            name='log',
            field=models.ForeignKey(related_name='monster_drops', to='sw_parser.RiftDungeonLog'),
        ),
    ]
