# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0089_auto_20160517_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='notes',
            field=models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled', null=True, blank=True),
        ),
    ]
