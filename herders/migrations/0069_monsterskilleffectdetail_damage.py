# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0068_auto_20160224_0929'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='damage',
            field=models.BooleanField(default=False, help_text=b'Amount of this effect is based on damage dealt'),
        ),
    ]
