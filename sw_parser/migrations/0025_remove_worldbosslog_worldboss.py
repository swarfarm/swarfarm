# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0024_shoprefreshlog_slots_available'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='worldbosslog',
            name='worldboss',
        ),
    ]
