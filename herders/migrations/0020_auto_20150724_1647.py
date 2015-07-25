# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0019_event'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Event',
            new_name='GameEvent',
        ),
    ]
