# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0060_runeinstance_efficiency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monster',
            name='awaken_ele_mats_high',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='awaken_ele_mats_low',
        ),
        migrations.RemoveField(
            model_name='monster',
            name='awaken_ele_mats_mid',
        ),
    ]
