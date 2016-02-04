# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0058_auto_20160201_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='random',
            field=models.BooleanField(default=False, help_text=b'Skill effect applies randomly to the target'),
        ),
    ]
