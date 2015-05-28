# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0005_auto_20150421_0008'),
    ]

    operations = [
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_ele_mats_large',
            new_name='awaken_ele_mats_high',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_ele_mats_small',
            new_name='awaken_ele_mats_low',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_ele_mats_med',
            new_name='awaken_ele_mats_mid',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_magic_mats_large',
            new_name='awaken_magic_mats_high',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_magic_mats_small',
            new_name='awaken_magic_mats_low',
        ),
        migrations.RenameField(
            model_name='monster',
            old_name='awaken_magic_mats_med',
            new_name='awaken_magic_mats_mid',
        ),
    ]
