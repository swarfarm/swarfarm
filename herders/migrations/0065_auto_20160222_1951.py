# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0064_auto_20160217_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='note',
            field=models.TextField(help_text=b"Explain anything else that doesn't fit in other fields", null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterskilleffectdetail',
            name='quantity',
            field=models.IntegerField(help_text=b'Number of items this effect affects on the target', null=True, blank=True),
        ),
    ]
