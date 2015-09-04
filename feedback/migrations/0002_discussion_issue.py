# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('feedback', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('comment', models.TextField()),
                ('feedback', models.ForeignKey(to='feedback.Feedback')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted', models.DateTimeField(auto_now=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Unreviewed'), (2, b'Accepted'), (3, b'In Progress'), (4, b'Requires Feedback'), (5, b'Resolved'), (6, b'Rejected')])),
                ('priority', models.IntegerField(blank=True, null=True, choices=[(1, b'Now'), (2, b'Soon'), (3, b'Someday')])),
                ('topic', models.IntegerField(choices=[(1, b'Errors or layout issues on website'), (2, b'Idea for new feature or improvement'), (3, b'Incorrect monster data'), (99, b'Other (Please be descriptive below')])),
                ('subject', models.CharField(max_length=40)),
                ('description', models.TextField()),
                ('public', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('status', 'priority', 'submitted'),
            },
        ),
    ]
