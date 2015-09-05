# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0033_auto_20150817_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='summoner',
            name='following',
            field=models.ManyToManyField(related_name='followed_by', to='herders.Summoner'),
        ),
    ]
