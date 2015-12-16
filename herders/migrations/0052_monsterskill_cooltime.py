# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0051_auto_20151215_1342'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskill',
            name='cooltime',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
