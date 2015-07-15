# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0002_auto_20150715_1235'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='display_until',
            new_name='frontpage_until',
        ),
    ]
