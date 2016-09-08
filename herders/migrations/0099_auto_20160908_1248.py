# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0098_monsterinstance_avg_rune_efficiency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='affected_stat',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'HP'), (1, b'ATK'), (2, b'DEF'), (3, b'SPD'), (4, b'CRI Rate'), (5, b'CRI Dmg'), (6, b'Resistance'), (7, b'Accuracy'), (8, b'Max. Energy'), (9, b'Mana Stone Storage'), (10, b'Mana Stone Production Rate'), (11, b'Energy Production Rate'), (12, b'Arcane Tower ATK'), (13, b'Arcane Tower SPD')]),
        ),
        migrations.AlterField(
            model_name='runecraftinstance',
            name='rune',
            field=models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy'), (17, b'Fight'), (18, b'Determination'), (19, b'Enhance'), (20, b'Accuracy'), (21, b'Tolerance')]),
        ),
        migrations.AlterField(
            model_name='runeinstance',
            name='type',
            field=models.IntegerField(choices=[(1, b'Energy'), (2, b'Fatal'), (3, b'Blade'), (4, b'Rage'), (5, b'Swift'), (6, b'Focus'), (7, b'Guard'), (8, b'Endure'), (9, b'Violent'), (10, b'Will'), (11, b'Nemesis'), (12, b'Shield'), (13, b'Revenge'), (14, b'Despair'), (15, b'Vampire'), (16, b'Destroy'), (17, b'Fight'), (18, b'Determination'), (19, b'Enhance'), (20, b'Accuracy'), (21, b'Tolerance')]),
        ),
    ]
