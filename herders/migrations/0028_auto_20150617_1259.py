# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0027_monsterinstance_in_storage'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='awakens_to',
            field=models.ForeignKey(related_name='+', blank=True, to='herders.Monster', null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awakens_from',
            field=models.ForeignKey(related_name='+', blank=True, to='herders.Monster', null=True),
        ),
    ]
