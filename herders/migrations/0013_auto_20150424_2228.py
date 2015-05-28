# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0012_auto_20150421_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_1_level',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_2_level',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_3_level',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='skill_4_level',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
