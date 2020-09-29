# Generated by Django 2.2.13 on 2020-07-31 18:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bestiary', '0024_auto_20200502_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameitem',
            name='category',
            field=models.IntegerField(choices=[(1, 'Monster'), (6, 'Currency'), (9, 'Summoning Scroll'), (10, 'Booster'), (11, 'Essence'), (12, 'Monster Piece'), (19, 'Guild Monster Piece'), (25, 'Rainbowmon'), (27, 'Rune Craft'), (29, 'Craft Material'), (30, 'Secret Dungeon'), (61, 'Enhancing Monster'), (73, 'Artifact'), (75, 'Artifact Craft Material')], help_text='Typically corresponds to `item_master_id` field'),
        ),
    ]