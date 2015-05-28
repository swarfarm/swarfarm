# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0016_auto_20150506_2247'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterinstance',
            name='fodder_for',
            field=models.ForeignKey(blank=True, to='herders.MonsterInstance', null=True),
        ),
    ]
