# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted', models.DateTimeField(auto_now_add=True)),
                ('status', models.IntegerField(default=1, choices=[(1, b'Unreviewed'), (2, b'Accepted'), (3, b'In Progress'), (4, b'Requires Feedback'), (5, b'Resolved'), (6, b'Rejected'), (7, b'Duplicate')])),
                ('priority', models.IntegerField(blank=True, null=True, choices=[(1, b'Now'), (2, b'Soon'), (3, b'Someday')])),
                ('topic', models.IntegerField(choices=[(1, b'Errors or layout issues on website'), (2, b'Idea for new feature or improvement'), (3, b'Incorrect monster data'), (99, b'Other')])),
                ('subject', models.CharField(max_length=40)),
                ('description', models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled')),
                ('public', models.BooleanField(default=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('status', 'priority', 'submitted'),
            },
        ),
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('comment', models.TextField(help_text=b'<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled')),
                ('feedback', models.ForeignKey(to='feedback.Issue')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('edited', models.DateTimeField(auto_now=True, null=True)),
            ],
            options={
                'ordering': ('timestamp',),
            },
        ),
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['submitted']},
        ),
        migrations.RemoveField(
            model_name='issue',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='issue',
            name='topic',
        ),
        migrations.AddField(
            model_name='issue',
            name='closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='issue',
            name='edited',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AddField(
            model_name='issue',
            name='github_issue_url',
            field=models.URLField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='public',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterModelOptions(
            name='issue',
            options={'ordering': ['-latest_comment']},
        ),
        migrations.RemoveField(
            model_name='issue',
            name='status',
        ),
        migrations.AddField(
            model_name='issue',
            name='latest_comment',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
