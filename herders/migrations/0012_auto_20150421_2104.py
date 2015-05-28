# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0011_remove_monster_icon'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monster',
            options={'ordering': ['name', 'element']},
        ),
        migrations.AddField(
            model_name='summoner',
            name='notes',
            field=models.TextField(blank=True),
        ),
    ]
