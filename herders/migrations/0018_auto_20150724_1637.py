# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0017_auto_20150714_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterleaderskill',
            name='attribute',
            field=models.IntegerField(choices=[(1, b'HP'), (2, b'Attack Power'), (3, b'Defense'), (4, b'Attack Speed'), (5, b'Critical Rate'), (6, b'Resistance'), (7, b'Accuracy'), (8, b'Critical DMG')]),
        ),
    ]
