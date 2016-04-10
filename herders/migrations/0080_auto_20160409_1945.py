# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0079_auto_20160407_1956'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monsterskilleffect',
            options={},
        ),
        migrations.AlterField(
            model_name='runecraftinstance',
            name='quality',
            field=models.IntegerField(choices=[(1, b'Magic'), (2, b'Rare'), (3, b'Hero'), (4, b'Legend')]),
        ),
    ]
