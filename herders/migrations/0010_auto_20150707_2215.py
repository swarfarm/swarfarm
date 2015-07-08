# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0009_auto_20150707_2156'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monster',
            name='skills',
            field=models.ManyToManyField(to='herders.MonsterSkill', blank=True),
        ),
    ]
