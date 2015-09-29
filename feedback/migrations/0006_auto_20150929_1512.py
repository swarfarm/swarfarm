# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0005_auto_20150920_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='submitted',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
