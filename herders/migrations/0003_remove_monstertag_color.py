# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0002_auto_20170402_2221'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monstertag',
            name='color',
        ),
    ]
