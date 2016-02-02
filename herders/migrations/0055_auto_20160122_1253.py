# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0054_auto_20160118_1623'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterPiece',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('pieces', models.IntegerField(default=0)),
                ('monster', models.ForeignKey(to='herders.Monster')),
                ('owner', models.ForeignKey(to='herders.Summoner')),
            ],
            options={
                'ordering': ['monster__name'],
            },
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='created',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
