# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0006_auto_20150421_0010'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='archetype',
            field=models.CharField(default=b'attack', max_length=10, choices=[(b'hp', b'HP'), (b'attack', b'Attack'), (b'support', b'Support'), (b'defense', b'Defense'), (b'material', b'Material')]),
        ),
    ]
