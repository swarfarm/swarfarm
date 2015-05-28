# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0017_monsterinstance_fodder_for'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterinstance',
            name='priority',
            field=models.IntegerField(default=1, choices=[(0, b'Done'), (1, b'Low'), (2, b'Medium'), (3, b'High')]),
        ),
    ]
