# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='leader',
            field=models.ForeignKey(related_name='team_leader', blank=True, to='herders.MonsterInstance', null=True),
        ),
    ]
