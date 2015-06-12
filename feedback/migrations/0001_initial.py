# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=120)),
                ('submitted', models.DateTimeField(auto_now=True)),
                ('subject', models.CharField(max_length=40)),
                ('feedback', models.TextField()),
            ],
        ),
    ]
