# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0008_runlog_energy'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runlog',
            name='energy',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
