# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0001_squashed_0109_runeinstance_original_quality'),
        ('bestiary', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('herders.building',),
        ),
    ]
