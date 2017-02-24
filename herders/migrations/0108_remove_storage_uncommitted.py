# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0107_auto_20170221_1245'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='storage',
            name='uncommitted',
        ),
    ]
