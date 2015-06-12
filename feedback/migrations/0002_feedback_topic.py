# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='feedback',
            name='topic',
            field=models.IntegerField(default=99, choices=[(1, b'Errors or layout issues on website'), (2, b'Idea for new feature or improvement'), (3, b'Incorrect monster data'), (99, b'Other (Please be descriptive below')]),
        ),
    ]
