# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0052_monsterskill_cooltime'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monsterinstance',
            options={'ordering': ['-stars', '-level', 'monster__name']},
        ),
        migrations.AlterModelOptions(
            name='runeinstance',
            options={'ordering': ['slot', 'type', 'level', 'quality']},
        ),
        migrations.AddField(
            model_name='monster',
            name='com2us_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='com2us_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='com2us_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='com2us_id',
            field=models.BigIntegerField(null=True, blank=True),
        ),
    ]
