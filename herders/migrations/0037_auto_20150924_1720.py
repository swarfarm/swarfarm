# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0036_monster_wikia_url'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runeinstance',
            name='monster',
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='runes',
            field=models.ForeignKey(blank=True, to='herders.RuneInstance', null=True),
        ),
    ]
