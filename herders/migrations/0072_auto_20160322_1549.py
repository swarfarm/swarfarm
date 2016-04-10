# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import colorfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0071_auto_20160224_1544'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('image', models.ImageField(upload_to=b'')),
                ('color', colorfield.fields.ColorField(max_length=10)),
            ],
        ),
        migrations.AddField(
            model_name='monsterinstance',
            name='tags',
            field=models.ManyToManyField(to='herders.MonsterTags'),
        ),
    ]
