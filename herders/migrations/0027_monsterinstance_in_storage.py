# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0026_remove_summoner_rep_monster'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterinstance',
            name='in_storage',
            field=models.BooleanField(default=False),
        ),
    ]
