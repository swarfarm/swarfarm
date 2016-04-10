# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0073_auto_20160322_1601'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monstertag',
            name='image',
        ),
    ]
