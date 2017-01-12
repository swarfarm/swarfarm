# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bestiary', '0003_delete_scaleswith'),
    ]

    operations = [
        migrations.CreateModel(
            name='PatchNotes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('major', models.IntegerField()),
                ('minor', models.IntegerField()),
                ('dev', models.IntegerField()),
                ('description', models.CharField(max_length=60, null=True, blank=True)),
                ('timestamp', models.DateTimeField()),
                ('detailed_notes', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
