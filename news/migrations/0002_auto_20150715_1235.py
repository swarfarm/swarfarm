# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-sticky', 'created')},
        ),
        migrations.AddField(
            model_name='article',
            name='sticky',
            field=models.BooleanField(default=False),
        ),
    ]
