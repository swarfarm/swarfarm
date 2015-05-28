# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0004_auto_20150421_0005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_large',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_med',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_small',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_magic_mats_large',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_magic_mats_med',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_magic_mats_small',
            field=models.IntegerField(null=True),
        ),
    ]
