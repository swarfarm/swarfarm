# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0014_auto_20150425_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterinstance',
            name='notes',
            field=models.TextField(null=True, blank=True),
        ),
    ]
