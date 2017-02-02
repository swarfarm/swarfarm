# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0104_auto_20160920_1111'),
        ('sw_parser', '0017_auto_20161013_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='RuneCraft',
            fields=[
                ('runedrop_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='sw_parser.RuneDrop')),
            ],
            bases=('sw_parser.runedrop',),
        ),
        migrations.CreateModel(
            name='RuneCraftLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('wizard_id', models.BigIntegerField()),
                ('timestamp', models.DateTimeField(null=True, blank=True)),
                ('server', models.IntegerField(blank=True, null=True, choices=[(0, b'Global'), (1, b'Europe'), (2, b'Asia'), (3, b'Korea'), (4, b'Japan'), (5, b'China')])),
                ('craft_level', models.IntegerField(choices=[(0, b'Low'), (1, b'Mid'), (2, b'High')])),
                ('summoner', models.ForeignKey(blank=True, to='herders.Summoner', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='runecraft',
            name='log',
            field=models.ForeignKey(to='sw_parser.RuneCraftLog'),
        ),
    ]
