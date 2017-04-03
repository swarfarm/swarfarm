# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0001_squashed_0109_runeinstance_original_quality'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='name',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='buildinginstance',
            name='building',
            field=models.ForeignKey(to='herders.Building'),
        ),
        migrations.AlterField(
            model_name='gameevent',
            name='all_day',
            field=models.BooleanField(),
        ),
    ]
