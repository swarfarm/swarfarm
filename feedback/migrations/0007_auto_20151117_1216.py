# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0006_auto_20150929_1512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='comment',
            field=models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='description',
            field=models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'),
        ),
    ]
