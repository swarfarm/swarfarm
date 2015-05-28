# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0008_auto_20150421_1926'),
    ]

    operations = [
        migrations.AddField(
            model_name='monster',
            name='can_awaken',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='archetype',
            field=models.CharField(default=b'attack', max_length=10, choices=[(b'attack', b'Attack'), (b'hp', b'HP'), (b'support', b'Support'), (b'defense', b'Defense'), (b'material', b'Material')]),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_ele_mats_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_magic_mats_high',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_magic_mats_low',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awaken_magic_mats_mid',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='awakens_from',
            field=models.ForeignKey(blank=True, to='herders.Monster', null=True),
        ),
    ]
