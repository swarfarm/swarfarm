# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0063_monsterskilleffectdetail_on_crit'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='on_death',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='monsterskilleffectdetail',
            name='on_crit',
            field=models.BooleanField(default=False),
        ),
    ]
