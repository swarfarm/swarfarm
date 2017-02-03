# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0007_auto_20151117_1216'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['submitted']},
        ),
        migrations.RemoveField(
            model_name='issue',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='topic',
        ),
        migrations.AddField(
            model_name='discussion',
            name='edited',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='issue',
            name='edited',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='github_issue_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='discussion',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
