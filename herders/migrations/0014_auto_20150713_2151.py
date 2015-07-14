# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0013_monsterinstance_ignore_for_fusion'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monsterskill',
            options={'ordering': ['name', 'icon_filename']},
        ),
        migrations.AlterModelOptions(
            name='monsterskilleffect',
            options={'ordering': ['-is_buff', 'name']},
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='element_leader',
            field=models.BooleanField(default=False),
        ),
    ]
