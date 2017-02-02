# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0023_dungeon_monster_slots'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoprefreshlog',
            name='slots_available',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
