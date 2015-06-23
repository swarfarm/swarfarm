# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0029_monster_image_filename'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fusion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stars', models.IntegerField()),
                ('cost', models.IntegerField()),
                ('ingredients', models.ManyToManyField(to='herders.Monster')),
                ('product', models.ForeignKey(related_name='product', to='herders.Monster')),
            ],
        ),
    ]
