# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0009_auto_20170203_1234'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['-latest_comment']},
        ),
        migrations.RemoveField(
            model_name='issue',
            name='status',
        ),
        migrations.AddField(
            model_name='issue',
            name='latest_comment',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
