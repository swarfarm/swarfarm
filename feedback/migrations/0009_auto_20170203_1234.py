# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0008_auto_20170202_2034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='public',
            field=models.BooleanField(default=True),
        ),
    ]
