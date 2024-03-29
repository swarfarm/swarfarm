# Generated by Django 2.2.28 on 2023-12-01 06:50

import bestiary.models.base
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('herders', '0036_auto_20231130_2250'),
        ('bestiary', '0036_delete_balancepatch'),
    ]

    operations = [
        migrations.CreateModel(
            name='LevelSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('com2us_id', models.IntegerField(db_index=True)),
                ('name', models.CharField(max_length=30)),
                ('max_level', models.IntegerField()),
                ('area', models.IntegerField(blank=True, choices=[(1, 'Battle'), (2, 'Guild content'), (3, 'Other')], null=True)),
                ('affected_stat', models.IntegerField(blank=True, choices=[(0, 'HP'), (1, 'ATK'), (2, 'DEF'), (3, 'SPD'), (4, 'CRI Rate'), (5, 'CRI Dmg'), (6, 'Resistance'), (7, 'Accuracy'), (8, 'Max. Energy'), (9, 'Mana Stone Storage'), (10, 'Mana Stone Production Rate'), (11, 'Energy Production Rate'), (12, 'Arcane Tower ATK'), (13, 'Arcane Tower SPD')], null=True)),
                ('element', models.CharField(blank=True, choices=[('pure', 'Pure'), ('fire', 'Fire'), ('wind', 'Wind'), ('water', 'Water'), ('light', 'Light'), ('dark', 'Dark'), ('intangible', 'Intangible')], max_length=6, null=True)),
                ('stat_bonus', django.contrib.postgres.fields.ArrayField(base_field=models.FloatField(blank=True, null=True), size=None)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            bases=(models.Model, bestiary.models.base.Elements),
        ),
        migrations.DeleteModel(
            name='Building',
        ),
        migrations.AlterField(
            model_name='gameitem',
            name='category',
            field=models.IntegerField(choices=[(1, 'Monster'), (6, 'Currency'), (9, 'Summoning Scroll'), (10, 'Booster'), (11, 'Essence'), (12, 'Monster Piece'), (19, 'Guild Monster Piece'), (25, 'Rainbowmon'), (27, 'Rune Craft'), (29, 'Craft Material'), (30, 'Secret Dungeon'), (61, 'Enhancing Monster'), (73, 'Artifact'), (75, 'Artifact Craft Material'), (82, 'Unknown Category')], db_index=True, help_text='Typically corresponds to `item_master_type` field'),
        ),
        migrations.AlterField(
            model_name='leaderskill',
            name='element',
            field=models.CharField(blank=True, choices=[('pure', 'Pure'), ('fire', 'Fire'), ('wind', 'Wind'), ('water', 'Water'), ('light', 'Light'), ('dark', 'Dark'), ('intangible', 'Intangible')], help_text='Element of monster which this leader skill applies to', max_length=6, null=True),
        ),
        migrations.AlterField(
            model_name='monster',
            name='archetype',
            field=models.CharField(choices=[('attack', 'Attack'), ('hp', 'HP'), ('support', 'Support'), ('defense', 'Defense'), ('material', 'Material'), ('intangible', 'Intangible')], default='attack', max_length=10),
        ),
        migrations.AlterField(
            model_name='monster',
            name='element',
            field=models.CharField(choices=[('pure', 'Pure'), ('fire', 'Fire'), ('wind', 'Wind'), ('water', 'Water'), ('light', 'Light'), ('dark', 'Dark'), ('intangible', 'Intangible')], default='fire', max_length=6),
        ),
    ]
