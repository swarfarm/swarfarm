# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0066_auto_20160222_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskillscaleswith',
            name='add_to_atk',
            field=models.BooleanField(default=False, help_text=b'Add value to ATK % value'),
        ),
    ]
