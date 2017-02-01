# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0007_auto_20160502_0911'),
    ]

    operations = [
        migrations.AddField(
            model_name='runlog',
            name='energy',
            field=models.IntegerField(default=0),
        ),
    ]
