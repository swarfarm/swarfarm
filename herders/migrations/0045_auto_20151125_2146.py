# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0044_auto_20151117_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='monsterinstance',
            name='base_accuracy',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_attack',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_crit_damage',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_crit_rate',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_defense',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_hp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_resistance',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='base_speed',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_accuracy',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_attack',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_crit_damage',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_crit_rate',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_defense',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_hp',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_resistance',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='rune_speed',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='monster',
            name='base_stars',
            field=models.IntegerField(choices=[(1, b'1<span class="glyphicon glyphicon-star"></span>'), (2, b'2<span class="glyphicon glyphicon-star"></span>'), (3, b'3<span class="glyphicon glyphicon-star"></span>'), (4, b'4<span class="glyphicon glyphicon-star"></span>'), (5, b'5<span class="glyphicon glyphicon-star"></span>'), (6, b'6<span class="glyphicon glyphicon-star"></span>')]),
        ),
    ]
