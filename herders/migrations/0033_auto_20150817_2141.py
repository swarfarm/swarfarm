# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0032_auto_20150805_1312'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monsterskill',
            options={'ordering': ['slot', 'name']},
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_1_level',
            field=models.IntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_2_level',
            field=models.IntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_3_level',
            field=models.IntegerField(default=1, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_4_level',
            field=models.IntegerField(default=1, blank=True),
        ),
    ]
