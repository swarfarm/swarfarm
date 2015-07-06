# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0003_auto_20150705_0103'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MonsterSkillEffects',
            new_name='MonsterSkillEffect',
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='general_leader',
            field=models.BooleanField(default=False),
        ),
    ]
