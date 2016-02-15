# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0061_auto_20160209_2121'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskill',
            name='hits',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='chance',
            field=models.IntegerField(help_text=b'Chance of effect occuring per hit', null=True, blank=True),
        ),
    ]
