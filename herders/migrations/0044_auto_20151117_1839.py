# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0043_auto_20151117_1216'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='arena_skill',
        ),
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='dungeon_skill',
        ),
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='element_skill',
        ),
        migrations.RemoveField(
            model_name='monsterleaderskill',
            name='guild_skill',
        ),
    ]
