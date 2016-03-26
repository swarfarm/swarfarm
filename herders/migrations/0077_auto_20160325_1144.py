# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0076_auto_20160323_2111'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='monstertag',
            options={'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='monstertag',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
