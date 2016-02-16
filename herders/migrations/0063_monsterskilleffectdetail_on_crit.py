# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0062_auto_20160215_1352'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterskilleffectdetail',
            name='on_crit',
            field=models.BooleanField(default=False, help_text=b'Effect occurs on critical hit'),
        ),
    ]
