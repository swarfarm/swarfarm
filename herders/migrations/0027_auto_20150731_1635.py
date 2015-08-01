# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0026_auto_20150727_1349'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('icon_filename', models.CharField(max_length=100, null=True, blank=True)),
                ('farmable_source', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='monster',
            name='source',
            field=models.ManyToManyField(to='herders.MonsterSource', blank=True),
        ),
    ]
