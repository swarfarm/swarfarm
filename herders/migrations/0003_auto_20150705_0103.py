# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0002_team_leader'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='team',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='teamgroup',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='team',
            name='roster',
            field=models.ManyToManyField(to='herders.MonsterInstance', blank=True),
        ),
    ]
