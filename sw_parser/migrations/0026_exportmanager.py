# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0025_remove_worldbosslog_worldboss'),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_name', models.TextField()),
                ('last_row', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
