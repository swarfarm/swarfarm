# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0005_auto_20150706_1421'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskill',
            name='slot',
            field=models.IntegerField(default=1),
        ),
    ]
