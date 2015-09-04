# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedback', '0002_discussion_issue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discussion',
            name='feedback',
            field=models.ForeignKey(to='feedback.Issue'),
        ),
        migrations.DeleteModel(
            name='Feedback',
        ),
    ]
