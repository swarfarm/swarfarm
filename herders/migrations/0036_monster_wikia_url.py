# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0035_monster_summonerswar_co_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='wikia_url',
            field=models.URLField(null=True, blank=True),
        ),
    ]
