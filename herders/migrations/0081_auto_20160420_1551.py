# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0080_auto_20160409_1945'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monsterskilleffect',
            options={'ordering': ['name']},
        ),
    ]
