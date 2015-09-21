# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0004_auto_20150903_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, b'Unreviewed'), (2, b'Accepted'), (3, b'In Progress'), (4, b'Requires Feedback'), (5, b'Resolved'), (6, b'Rejected'), (7, b'Duplicate')]),
        ),
    ]
