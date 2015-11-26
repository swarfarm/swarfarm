# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0045_auto_20151125_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_accuracy',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_attack',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_crit_damage',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_crit_rate',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_defense',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_hp',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_resistance',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='base_speed',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_accuracy',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_attack',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_crit_damage',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_crit_rate',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_defense',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_hp',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_resistance',
            field=models.IntegerField(default=0, blank=True),
        ),
        migrations.AlterField(
            model_name='monsterinstance',
            name='rune_speed',
            field=models.IntegerField(default=0, blank=True),
        ),
    ]
