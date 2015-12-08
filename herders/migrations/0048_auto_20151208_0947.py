# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('herders', '0047_auto_20151203_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='awaken_bonus_content_id',
            field=models.PositiveIntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='awaken_bonus_content_type',
            field=models.ForeignKey(related_name='content_type_awaken_bonus', blank=True, to='contenttypes.ContentType', null=True),
        ),
    ]
