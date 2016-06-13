# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0092_auto_20160608_2153'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='family_id',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='multiplier_formula_raw',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monsterskillscalingstat',
            name='description',
            field=models.TextField(null=True, blank=True),
        ),
    ]
