# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0003_auto_20150831_1749'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issue',
            name='topic',
            field=models.IntegerField(choices=[(1, b'Errors or layout issues on website'), (2, b'Idea for new feature or improvement'), (3, b'Incorrect monster data'), (99, b'Other')]),
        ),
    ]
