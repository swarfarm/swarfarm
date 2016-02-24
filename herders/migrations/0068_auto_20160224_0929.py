# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0067_monsterskillscaleswith_add_to_atk'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='self_hp',
            field=models.BooleanField(default=False, help_text=b"Amount of this effect is based on casting monster's HP"),
        ),
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='target_hp',
            field=models.BooleanField(default=False, help_text=b"Amount of this effect is based on target monster's HP"),
        ),
    ]
