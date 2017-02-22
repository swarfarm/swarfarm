# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0106_auto_20170130_2017'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monsterinstance',
            name='uncommitted',
        ),
        migrations.RemoveField(
            model_name='monsterpiece',
            name='uncommitted',
        ),
        migrations.RemoveField(
            model_name='runecraftinstance',
            name='uncommitted',
        ),
        migrations.RemoveField(
            model_name='runeinstance',
            name='uncommitted',
        ),
    ]
