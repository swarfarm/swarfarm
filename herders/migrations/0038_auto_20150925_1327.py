# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0037_auto_20150924_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monsterinstance',
            name='runes',
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='assigned_to',
            field=models.ForeignKey(blank=True, to='herders.MonsterInstance', null=True),
        ),
    ]
