# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0104_auto_20160920_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='summonerswarmonsters_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
