# Generated by Django 2.2.9 on 2020-01-27 06:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bestiary', '0019_skillupgrade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='monster',
            name='base_stars',
            field=models.IntegerField(choices=[(1, '1⭐'), (2, '2⭐'), (3, '3⭐'), (4, '4⭐'), (5, '5⭐'), (6, '6⭐')], help_text='Display stars in game'),
        ),
        migrations.AlterField(
            model_name='monster',
            name='natural_stars',
            field=models.IntegerField(choices=[(1, '1⭐'), (2, '2⭐'), (3, '3⭐'), (4, '4⭐'), (5, '5⭐'), (6, '6⭐')], help_text="Stars of the monster's lowest awakened form"),
        ),
        migrations.CreateModel(
            name='AwakenCost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField()),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bestiary.GameItem')),
                ('monster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='awaken_materials', to='bestiary.Monster')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]