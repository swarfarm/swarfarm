# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0078_runecraftinstance'),
    ]

    operations = [
        migrations.AddField(
            model_name='runeinstance',
            name='substat_1_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_2_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_3_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
        migrations.AddField(
            model_name='runeinstance',
            name='substat_4_craft',
            field=models.IntegerField(blank=True, null=True, choices=[(0, b'Grindstone'), (1, b'Enchant Gem')]),
        ),
    ]
