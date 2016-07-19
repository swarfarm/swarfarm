# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0095_auto_20160718_1305'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='runeinstance',
            name='has_substat_upgrades',
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_upgrades_remaining',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
