# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0099_auto_20160908_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uncommitted', models.BooleanField(default=False)),
                ('magic_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], base_field=models.IntegerField(default=0), size=3)),
                ('fire_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], base_field=models.IntegerField(default=0), size=3)),
                ('water_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], base_field=models.IntegerField(default=0), size=3)),
                ('wind_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], base_field=models.IntegerField(default=0), size=3)),
                ('light_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], base_field=models.IntegerField(default=0), size=3)),
                ('dark_essence', django.contrib.postgres.fields.ArrayField(default=[0, 0, 0], base_field=models.IntegerField(default=0), size=3)),
                ('wood', models.IntegerField(default=0)),
                ('leather', models.IntegerField(default=0)),
                ('rock', models.IntegerField(default=0)),
                ('ore', models.IntegerField(default=0)),
                ('mithril', models.IntegerField(default=0)),
                ('cloth', models.IntegerField(default=0)),
                ('rune_piece', models.IntegerField(default=0)),
                ('dust', models.IntegerField(default=0)),
                ('symbol_harmony', models.IntegerField(default=0)),
                ('symbol_transcendance', models.IntegerField(default=0)),
                ('symbol_chaos', models.IntegerField(default=0)),
                ('crystal_water', models.IntegerField(default=0)),
                ('crystal_fire', models.IntegerField(default=0)),
                ('crystal_wind', models.IntegerField(default=0)),
                ('crystal_light', models.IntegerField(default=0)),
                ('crystal_dark', models.IntegerField(default=0)),
                ('crystal_magic', models.IntegerField(default=0)),
                ('crystal_pure', models.IntegerField(default=0)),
                ('owner', models.OneToOneField(to='herders.Summoner')),
            ],
        ),
    ]
