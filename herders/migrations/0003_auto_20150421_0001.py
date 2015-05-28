# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0002_monster_fusion_food'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='awakens_to',
            field=models.ForeignKey(to='herders.Monster', null=True),
        ),
        migrations.AddField(
            model_name='monster',
            name='is_awakened',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='food',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='notes',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='element',
            field=models.CharField(default=b'fire', max_length=6, choices=[(b'fire', b'Fire'), (b'wind', b'Wind'), (b'water', b'Water'), (b'light', b'Light'), (b'dark', b'Dark')]),
        ),
    ]
