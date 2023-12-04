from django.contrib.postgres.fields import ArrayField
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from . import base

ESSENCE_MAP = {
    'magic': {
        'low': 11006,
        'mid': 12006,
        'high': 13006,
    },
    'water': {
        'low': 11001,
        'mid': 12001,
        'high': 13001,
    },
    'fire': {
        'low': 11002,
        'mid': 12002,
        'high': 13002,
    },
    'wind': {
        'low': 11003,
        'mid': 12003,
        'high': 13003,
    },
    'light': {
        'low': 11004,
        'mid': 12004,
        'high': 13004,
    },
    'dark': {
        'low': 11005,
        'mid': 12005,
        'high': 13005,
    },
}

class GameItem(models.Model):
    CATEGORY_MONSTER = 1
    CATEGORY_CURRENCY = 6
    CATEGORY_RUNE = 8
    CATEGORY_SUMMON_SCROLL = 9
    CATEGORY_BOOSTER = 10
    CATEGORY_ESSENCE = 11
    CATEGORY_MONSTER_PIECE = 12
    CATEOGRY_GUILD_MONSTER_PIECE = 19
    CATEGORY_RAINBOWMON = 25
    CATEGORY_RUNE_CRAFT = 27
    CATEGORY_CRAFT_STUFF = 29
    CATEGORY_SECRET_DUNGEON = 30
    CATEGORY_MATERIAL_MONSTER = 61
    CATEGORY_ARTIFACT = 73
    CATEGORY_ARTIFACT_CRAFT = 75
    CATEGORY_UNKNOWN = 82

    CATEGORY_CHOICES = (
        (CATEGORY_MONSTER, 'Monster'),
        (CATEGORY_CURRENCY, 'Currency'),
        (CATEGORY_SUMMON_SCROLL, 'Summoning Scroll'),
        (CATEGORY_BOOSTER, 'Booster'),
        (CATEGORY_ESSENCE, 'Essence'),
        (CATEGORY_MONSTER_PIECE, 'Monster Piece'),
        (CATEOGRY_GUILD_MONSTER_PIECE, 'Guild Monster Piece'),
        (CATEGORY_RAINBOWMON, 'Rainbowmon'),
        (CATEGORY_RUNE_CRAFT, 'Rune Craft'),
        (CATEGORY_CRAFT_STUFF, 'Craft Material'),
        (CATEGORY_SECRET_DUNGEON, 'Secret Dungeon'),
        (CATEGORY_MATERIAL_MONSTER, 'Enhancing Monster'),
        (CATEGORY_ARTIFACT, 'Artifact'),
        (CATEGORY_ARTIFACT_CRAFT, 'Artifact Craft Material'),
        (CATEGORY_UNKNOWN, 'Unknown Category'),
    )

    com2us_id = models.IntegerField(db_index=True)
    category = models.IntegerField(db_index=True, choices=CATEGORY_CHOICES, help_text='Typically corresponds to `item_master_type` field')
    name = models.CharField(max_length=200)
    icon = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, default='')
    slug = models.CharField(max_length=200)
    sell_value = models.IntegerField(blank=True, null=True)

    class Meta:
        unique_together = (
            'com2us_id',
            'category',
        )
        ordering = (
            'category',
            'com2us_id',
        )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def image_tag(self):
        if self.icon:
            path = static('herders/images/items/' + self.icon)
            return mark_safe(f'<img src="{path}" height="42" width="42" loading="lazy" />')
        else:
            return 'No Image'


class ItemQuantity(models.Model):
    # Abstract model for representing quantities of items for various purposes
    item = models.ForeignKey(GameItem, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.item.name} - qty. {self.quantity}'

    class Meta:
        abstract = True


class LevelSkill(models.Model, base.Elements):
    AREA_BATTLE = 1
    AREA_GUILD = 2
    AREA_OTHER = 3

    AREA_CHOICES = [
        (AREA_BATTLE, 'Battle'),
        (AREA_GUILD, 'Guild content'),
        (AREA_OTHER, 'Other'),
    ]

    STAT_HP = 0
    STAT_ATK = 1
    STAT_DEF = 2
    STAT_SPD = 3
    STAT_CRIT_RATE_PCT = 4
    STAT_CRIT_DMG_PCT = 5
    STAT_RESIST_PCT = 6
    STAT_ACCURACY_PCT = 7
    MAX_ENERGY = 8
    MANA_STONE_STORAGE = 9
    MANA_STONE_PRODUCTION = 10
    ENERGY_PRODUCTION = 11
    ARCANE_TOWER_ATK = 12
    ARCANE_TOWER_SPD = 13

    STAT_CHOICES = [
        (STAT_HP, 'HP'),
        (STAT_ATK, 'ATK'),
        (STAT_DEF, 'DEF'),
        (STAT_SPD, 'SPD'),
        (STAT_CRIT_RATE_PCT, 'CRI Rate'),
        (STAT_CRIT_DMG_PCT, 'CRI Dmg'),
        (STAT_RESIST_PCT, 'Resistance'),
        (STAT_ACCURACY_PCT, 'Accuracy'),
        (MAX_ENERGY, 'Max. Energy'),
        (MANA_STONE_STORAGE, 'Mana Stone Storage'),
        (MANA_STONE_PRODUCTION, 'Mana Stone Production Rate'),
        (ENERGY_PRODUCTION, 'Energy Production Rate'),
        (ARCANE_TOWER_ATK, 'Arcane Tower ATK'),
        (ARCANE_TOWER_SPD, 'Arcane Tower SPD'),
    ]

    PERCENT_STATS = [
        STAT_HP,
        STAT_ATK,
        STAT_DEF,
        STAT_SPD,
        STAT_CRIT_RATE_PCT,
        STAT_CRIT_DMG_PCT,
        STAT_RESIST_PCT,
        STAT_ACCURACY_PCT,
        MANA_STONE_PRODUCTION,
        ENERGY_PRODUCTION,
        ARCANE_TOWER_ATK,
        ARCANE_TOWER_SPD,
    ]

    com2us_id = models.IntegerField(db_index=True)
    name = models.CharField(max_length=30)
    max_level = models.IntegerField()
    area = models.IntegerField(choices=AREA_CHOICES, null=True, blank=True)
    affected_stat = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    element = models.CharField(max_length=10, choices=base.Elements.ELEMENT_CHOICES, blank=True, null=True)
    stat_bonus = ArrayField(models.FloatField(blank=True, null=True))
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    icon_filename = models.CharField(max_length=100, null=True, blank=True)
    farmable_source = models.BooleanField(default=False)
    meta_order = models.IntegerField(db_index=True, default=0)

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42" loading="lazy" />' % static('herders/images/icons/' + self.icon_filename))
        else:
            return 'No Image'

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['meta_order', 'icon_filename', 'name']


