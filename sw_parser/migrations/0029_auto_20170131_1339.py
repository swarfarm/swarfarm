# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sw_parser', '0028_auto_20170131_1149'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runecraft',
            name='log',
            field=models.ForeignKey(related_name='rune', to='sw_parser.RuneCraftLog'),
        ),
        migrations.AlterField(
            model_name='shoprefreshitem',
            name='log',
            field=models.ForeignKey(related_name='item_drops', to='sw_parser.ShopRefreshLog'),
        ),
        migrations.AlterField(
            model_name='shoprefreshmonster',
            name='log',
            field=models.ForeignKey(related_name='monster_drops', to='sw_parser.ShopRefreshLog'),
        ),
        migrations.AlterField(
            model_name='shoprefreshrune',
            name='log',
            field=models.ForeignKey(related_name='rune_drops', to='sw_parser.ShopRefreshLog'),
        ),
        migrations.AlterField(
            model_name='worldbossitemdrop',
            name='log',
            field=models.ForeignKey(related_name='item_drops', to='sw_parser.WorldBossLog'),
        ),
        migrations.AlterField(
            model_name='worldbossmonsterdrop',
            name='log',
            field=models.ForeignKey(related_name='monster_drops', to='sw_parser.WorldBossLog'),
        ),
        migrations.AlterField(
            model_name='worldbossrunedrop',
            name='log',
            field=models.ForeignKey(related_name='rune_drops', to='sw_parser.WorldBossLog'),
        ),
    ]
