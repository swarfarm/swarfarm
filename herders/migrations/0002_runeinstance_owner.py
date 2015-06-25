# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='owner',
            field=models.ForeignKey(to='herders.Summoner', null=True),
        ),
    ]
