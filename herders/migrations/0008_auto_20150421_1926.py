# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0007_monster_archetype'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monster',
            name='awakens_to',
        ),
        migrations.AddField(
            model_name='monster',
            name='awakens_from',
            field=models.ForeignKey(to='herders.Monster', null=True),
        ),
    ]
