# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0039_auto_20150925_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='bestiary_slug',
            field=models.SlugField(max_length=255, null=True, editable=False),
        ),
    ]
