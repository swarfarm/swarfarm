# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60)),
                ('body', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('display_until', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='article',
            options={'ordering': ('-sticky', 'created')},
        ),
        migrations.AddField(
            model_name='article',
            name='sticky',
            field=models.BooleanField(default=False),
        ),
        migrations.RenameField(
            model_name='article',
            old_name='display_until',
            new_name='frontpage_until',
        ),
        migrations.RemoveField(
            model_name='article',
            name='frontpage_until',
        ),
        migrations.AlterField(
            model_name='article',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
