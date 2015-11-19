# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0042_auto_20151014_1341'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterleaderskill',
            name='area',
            field=models.IntegerField(default=1, choices=[(1, b'General'), (2, b'Dungeon'), (3, b'Element'), (4, b'Arena'), (5, b'Guild')]),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='notes',
            field=models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='team',
            name='description',
            field=models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled', null=True, blank=True),
        ),
    ]
