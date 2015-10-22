# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0040_monster_bestiary_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='quality',
            field=models.IntegerField(default=0),
        ),
    ]
