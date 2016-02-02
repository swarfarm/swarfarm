# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0056_monsterpiece_uncommitted'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterSkillEffectDetail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('aoe', models.BooleanField(default=False, help_text=b'Effect applies to entire friendly or enemy group')),
                ('single_target', models.BooleanField(default=False, help_text=b'Effect applies to a single monster')),
                ('self_effect', models.BooleanField(default=False, help_text=b'Effect applies to the monster using the skill')),
                ('quantity', models.IntegerField(default=0, help_text=b'Number of items this effect affects on the target')),
                ('all', models.BooleanField(default=False, help_text=b'This effect affects all items on the target')),
                ('effect', models.ForeignKey(to='herders.MonsterSkillEffect')),
                ('skill', models.ForeignKey(to='herders.MonsterSkill')),
            ],
        ),
        migrations.AddField(
            model_name='monsterskill',
            name='effect',
            field=models.ManyToManyField(related_name='effect', through='herders.MonsterSkillEffectDetail', to='herders.MonsterSkillEffect', blank=True),
        ),
    ]
