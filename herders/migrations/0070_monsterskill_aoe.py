# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0069_monsterskilleffectdetail_damage'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskill',
            name='aoe',
            field=models.BooleanField(default=False),
        ),
    ]
