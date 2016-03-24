# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0074_remove_monstertag_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monsterinstance',
            name='tags',
            field=models.ManyToManyField(to='herders.MonsterTag', blank=True),
        ),
    ]
