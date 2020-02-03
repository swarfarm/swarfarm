from collections import OrderedDict
from enum import IntEnum

from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from . import base
from .items import CraftMaterial, ItemQuantity


class Monster(models.Model, base.Elements):
    TYPE_ATTACK = 'attack'
    TYPE_HP = 'hp'
    TYPE_SUPPORT = 'support'
    TYPE_DEFENSE = 'defense'
    TYPE_MATERIAL = 'material'
    TYPE_NONE = 'none'

    TYPE_CHOICES = (
        (TYPE_NONE, 'None'),
        (TYPE_ATTACK, 'Attack'),
        (TYPE_HP, 'HP'),
        (TYPE_SUPPORT, 'Support'),
        (TYPE_DEFENSE, 'Defense'),
        (TYPE_MATERIAL, 'Material'),
    )

    STAR_CHOICES = (
        (1, '1⭐'),
        (2, '2⭐'),
        (3, '3⭐'),
        (4, '4⭐'),
        (5, '5⭐'),
        (6, '6⭐'),
    )

    AWAKEN_LEVEL_INCOMPLETE = -1  # Japan fusion
    AWAKEN_LEVEL_UNAWAKENED = 0
    AWAKEN_LEVEL_AWAKENED = 1
    AWAKEN_LEVEL_SECOND = 2

    AWAKEN_CHOICES = (
        (AWAKEN_LEVEL_UNAWAKENED, 'Unawakened'),
        (AWAKEN_LEVEL_AWAKENED, 'Awakened'),
        (AWAKEN_LEVEL_SECOND, 'Second Awakening'),
        (AWAKEN_LEVEL_INCOMPLETE, 'Incomplete'),
    )

    # Mappings from com2us' API data to model defined values
    COM2US_ARCHETYPE_MAP = {
        0: TYPE_NONE,
        1: TYPE_ATTACK,
        2: TYPE_DEFENSE,
        3: TYPE_HP,
        4: TYPE_SUPPORT,
        5: TYPE_MATERIAL
    }

    COM2US_AWAKEN_MAP = {
        -1: AWAKEN_LEVEL_INCOMPLETE,
        0: AWAKEN_LEVEL_UNAWAKENED,
        1: AWAKEN_LEVEL_AWAKENED,
        2: AWAKEN_LEVEL_SECOND,
    }

    name = models.CharField(max_length=40)
    com2us_id = models.IntegerField(blank=True, null=True, help_text='ID given in game data files')
    family_id = models.IntegerField(blank=True, null=True, help_text='Identifier that matches same family monsters')
    image_filename = models.CharField(max_length=250, null=True, blank=True)
    element = models.CharField(max_length=6, choices=base.Elements.ELEMENT_CHOICES, default=base.Elements.ELEMENT_FIRE)
    archetype = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_ATTACK)
    base_stars = models.IntegerField(choices=STAR_CHOICES, help_text='Display stars in game')
    natural_stars = models.IntegerField(choices=STAR_CHOICES, help_text="Stars of the monster's lowest awakened form")
    obtainable = models.BooleanField(default=True, help_text='Is available for players to acquire')
    can_awaken = models.BooleanField(default=True, help_text='Has an awakened form')
    is_awakened = models.BooleanField(default=False, help_text='Is the awakened form')
    awaken_level = models.IntegerField(default=AWAKEN_LEVEL_UNAWAKENED, choices=AWAKEN_CHOICES, help_text='Awakening level')
    awaken_bonus = models.TextField(blank=True, help_text='Bonus given upon awakening')

    skills = models.ManyToManyField('Skill', blank=True)
    skill_ups_to_max = models.IntegerField(null=True, blank=True, help_text='Number of skill-ups required to max all skills')
    leader_skill = models.ForeignKey('LeaderSkill', on_delete=models.SET_NULL, null=True, blank=True)

    # 1-star lvl 1 values from data source
    raw_hp = models.IntegerField(null=True, blank=True, help_text='HP value from game data files')
    raw_attack = models.IntegerField(null=True, blank=True, help_text='ATK value from game data files')
    raw_defense = models.IntegerField(null=True, blank=True, help_text='DEF value from game data files')

    # Base-star lvl MAX values as seen in-game
    base_hp = models.IntegerField(null=True, blank=True, help_text='HP at base_stars lvl 1')
    base_attack = models.IntegerField(null=True, blank=True, help_text='ATK at base_stars lvl 1')
    base_defense = models.IntegerField(null=True, blank=True, help_text='DEF at base_stars lvl 1')

    # 6-star lvl MAX values
    max_lvl_hp = models.IntegerField(null=True, blank=True, help_text='HP at 6-stars lvl 40')
    max_lvl_attack = models.IntegerField(null=True, blank=True, help_text='ATK at 6-stars lvl 40')
    max_lvl_defense = models.IntegerField(null=True, blank=True, help_text='DEF at 6-stars lvl 40')

    speed = models.IntegerField(null=True, blank=True)
    crit_rate = models.IntegerField(null=True, blank=True)
    crit_damage = models.IntegerField(null=True, blank=True)
    resistance = models.IntegerField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)

    # Homunculus monster fields
    homunculus = models.BooleanField(default=False)
    craft_materials = models.ManyToManyField('CraftMaterial', through='MonsterCraftCost')
    craft_cost = models.IntegerField(null=True, blank=True, help_text='Mana cost to craft this monster')

    # Unicorn fields
    transforms_into = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', help_text='Monster which this monster can transform into during battle')

    awakens_from = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', help_text='Unawakened form of this monster')
    awakens_to = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='+', help_text='Awakened form of this monster')
    awaken_mats_fire_low = models.IntegerField(blank=True, default=0)
    awaken_mats_fire_mid = models.IntegerField(blank=True, default=0)
    awaken_mats_fire_high = models.IntegerField(blank=True, default=0)
    awaken_mats_water_low = models.IntegerField(blank=True, default=0)
    awaken_mats_water_mid = models.IntegerField(blank=True, default=0)
    awaken_mats_water_high = models.IntegerField(blank=True, default=0)
    awaken_mats_wind_low = models.IntegerField(blank=True, default=0)
    awaken_mats_wind_mid = models.IntegerField(blank=True, default=0)
    awaken_mats_wind_high = models.IntegerField(blank=True, default=0)
    awaken_mats_light_low = models.IntegerField(blank=True, default=0)
    awaken_mats_light_mid = models.IntegerField(blank=True, default=0)
    awaken_mats_light_high = models.IntegerField(blank=True, default=0)
    awaken_mats_dark_low = models.IntegerField(blank=True, default=0)
    awaken_mats_dark_mid = models.IntegerField(blank=True, default=0)
    awaken_mats_dark_high = models.IntegerField(blank=True, default=0)
    awaken_mats_magic_low = models.IntegerField(blank=True, default=0)
    awaken_mats_magic_mid = models.IntegerField(blank=True, default=0)
    awaken_mats_magic_high = models.IntegerField(blank=True, default=0)

    source = models.ManyToManyField('Source', blank=True, help_text='Where this monster can be acquired from')
    farmable = models.BooleanField(default=False, help_text='Monster can be acquired easily without luck')
    fusion_food = models.BooleanField(default=False, help_text='Monster is used as a fusion ingredient')
    bestiary_slug = models.SlugField(max_length=255, editable=False, null=True)

    def image_url(self):
        if self.image_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/monsters/' + self.image_filename))
        else:
            return 'No Image'

    def max_level_from_stars(self, stars=None):
        if stars:
            return 10 + stars * 5
        else:
            return 10 + self.base_stars * 5

    def get_stats(self):
        from collections import OrderedDict

        start_grade = self.base_stars
        stats_list = OrderedDict()

        if self.is_awakened and self.base_stars > 1:
            start_grade -= 1

        for grade in range(start_grade, 7):
            max_level = self.max_level_from_stars(grade)

            # Add the actual calculated stats
            stats_list[str(grade)] = {
                'HP': self.actual_hp(grade, max_level),
                'ATK': self.actual_attack(grade, max_level),
                'DEF': self.actual_defense(grade, max_level),
            }

        return stats_list

    def actual_hp(self, grade, level):
        # Check that base stat exists first
        if not self.raw_hp:
            return None
        else:
            return self._calculate_actual_stat(self.raw_hp, grade, level) * 15

    def actual_attack(self, grade=base_stars, level=1):
        # Check that base stat exists first
        if not self.raw_attack:
            return None
        else:
            return self._calculate_actual_stat(self.raw_attack, grade, level)

    def actual_defense(self, grade=base_stars, level=1):
        # Check that base stat exists first
        if not self.raw_defense:
            return None
        else:
            return self._calculate_actual_stat(self.raw_defense, grade, level)

    @staticmethod
    def _calculate_actual_stat(stat, grade, level):
        # Magic multipliers taken from summoner's war wikia calculator. Used to calculate stats for lvl 1 and lvl MAX
        magic_multipliers = [
            {'1': 1.0, 'max': 1.9958},
            {'1': 1.5966, 'max': 3.03050646},
            {'1': 2.4242774, 'max': 4.364426603},
            {'1': 3.4914444, 'max': 5.941390935},
            {'1': 4.7529032, 'max': 8.072330795},
            {'1': 6.4582449, 'max': 10.97901633},
        ]

        max_lvl = 10 + grade * 5
        stat_lvl_1 = round(stat * magic_multipliers[grade - 1]['1'], 0)
        stat_lvl_max = round(stat * magic_multipliers[grade - 1]['max'], 0)

        if level == 1:
            return int(stat_lvl_1)
        elif level == max_lvl:
            return int(stat_lvl_max)
        else:
            # Use exponential function in format value=ae^(bx)
            # a=stat_lvl_1*e^(-b)
            from math import log, exp
            b_coeff = log(stat_lvl_max / stat_lvl_1) / (max_lvl - 1)

            return int(round((stat_lvl_1 * exp(-b_coeff)) * exp(b_coeff * level)))

    @property
    def base_monster(self):
        if self.awakens_from is not None and self.awakens_from.obtainable:
            return self.awakens_from.base_monster

        return self

    def monster_family(self):
        should_be_shown = Q(obtainable=True) | Q(transforms_into__isnull=False)
        has_awakened_version = Q(can_awaken=True) & Q(awakens_to__isnull=False)
        return Monster.objects.filter(should_be_shown, family_id=self.family_id).exclude(has_awakened_version).order_by('com2us_id')

    def get_awakening_materials(self):
        mats = OrderedDict()
        mats['magic'] = OrderedDict()
        mats['magic']['low'] = self.awaken_mats_magic_low
        mats['magic']['mid'] = self.awaken_mats_magic_mid
        mats['magic']['high'] = self.awaken_mats_magic_high
        mats['fire'] = OrderedDict()
        mats['fire']['low'] = self.awaken_mats_fire_low
        mats['fire']['mid'] = self.awaken_mats_fire_mid
        mats['fire']['high'] = self.awaken_mats_fire_high
        mats['water'] = OrderedDict()
        mats['water']['low'] = self.awaken_mats_water_low
        mats['water']['mid'] = self.awaken_mats_water_mid
        mats['water']['high'] = self.awaken_mats_water_high
        mats['wind'] = OrderedDict()
        mats['wind']['low'] = self.awaken_mats_wind_low
        mats['wind']['mid'] = self.awaken_mats_wind_mid
        mats['wind']['high'] = self.awaken_mats_wind_high
        mats['light'] = OrderedDict()
        mats['light']['low'] = self.awaken_mats_light_low
        mats['light']['mid'] = self.awaken_mats_light_mid
        mats['light']['high'] = self.awaken_mats_light_high
        mats['dark'] = OrderedDict()
        mats['dark']['low'] = self.awaken_mats_dark_low
        mats['dark']['mid'] = self.awaken_mats_dark_mid
        mats['dark']['high'] = self.awaken_mats_dark_high

        return mats

    def clean(self):
        # Update null values
        if self.awaken_mats_fire_high is None:
            self.awaken_mats_fire_high = 0
        if self.awaken_mats_fire_mid is None:
            self.awaken_mats_fire_mid = 0
        if self.awaken_mats_fire_low is None:
            self.awaken_mats_fire_low = 0
        if self.awaken_mats_water_high is None:
            self.awaken_mats_water_high = 0
        if self.awaken_mats_water_mid is None:
            self.awaken_mats_water_mid = 0
        if self.awaken_mats_water_low is None:
            self.awaken_mats_water_low = 0
        if self.awaken_mats_wind_high is None:
            self.awaken_mats_wind_high = 0
        if self.awaken_mats_wind_mid is None:
            self.awaken_mats_wind_mid = 0
        if self.awaken_mats_wind_low is None:
            self.awaken_mats_wind_low = 0
        if self.awaken_mats_light_high is None:
            self.awaken_mats_light_high = 0
        if self.awaken_mats_light_mid is None:
            self.awaken_mats_light_mid = 0
        if self.awaken_mats_light_low is None:
            self.awaken_mats_light_low = 0
        if self.awaken_mats_dark_high is None:
            self.awaken_mats_dark_high = 0
        if self.awaken_mats_dark_mid is None:
            self.awaken_mats_dark_mid = 0
        if self.awaken_mats_dark_low is None:
            self.awaken_mats_dark_low = 0
        if self.awaken_mats_magic_high is None:
            self.awaken_mats_magic_high = 0
        if self.awaken_mats_magic_mid is None:
            self.awaken_mats_magic_mid = 0
        if self.awaken_mats_magic_low is None:
            self.awaken_mats_magic_low = 0

        super(Monster, self).clean()

    def save(self, *args, **kwargs):
        # Update null values
        if self.awaken_mats_fire_high is None:
            self.awaken_mats_fire_high = 0
        if self.awaken_mats_fire_mid is None:
            self.awaken_mats_fire_mid = 0
        if self.awaken_mats_fire_low is None:
            self.awaken_mats_fire_low = 0
        if self.awaken_mats_water_high is None:
            self.awaken_mats_water_high = 0
        if self.awaken_mats_water_mid is None:
            self.awaken_mats_water_mid = 0
        if self.awaken_mats_water_low is None:
            self.awaken_mats_water_low = 0
        if self.awaken_mats_wind_high is None:
            self.awaken_mats_wind_high = 0
        if self.awaken_mats_wind_mid is None:
            self.awaken_mats_wind_mid = 0
        if self.awaken_mats_wind_low is None:
            self.awaken_mats_wind_low = 0
        if self.awaken_mats_light_high is None:
            self.awaken_mats_light_high = 0
        if self.awaken_mats_light_mid is None:
            self.awaken_mats_light_mid = 0
        if self.awaken_mats_light_low is None:
            self.awaken_mats_light_low = 0
        if self.awaken_mats_dark_high is None:
            self.awaken_mats_dark_high = 0
        if self.awaken_mats_dark_mid is None:
            self.awaken_mats_dark_mid = 0
        if self.awaken_mats_dark_low is None:
            self.awaken_mats_dark_low = 0
        if self.awaken_mats_magic_high is None:
            self.awaken_mats_magic_high = 0
        if self.awaken_mats_magic_mid is None:
            self.awaken_mats_magic_mid = 0
        if self.awaken_mats_magic_low is None:
            self.awaken_mats_magic_low = 0

        if self.raw_hp:
            self.base_hp = self._calculate_actual_stat(
                self.raw_hp,
                self.base_stars,
                self.max_level_from_stars(self.base_stars)
            ) * 15
            self.max_lvl_hp = self.actual_hp(6, 40)

        if self.raw_attack:
            self.base_attack = self._calculate_actual_stat(
                self.raw_attack,
                self.base_stars,
                self.max_level_from_stars(self.base_stars)
            )
            self.max_lvl_attack = self.actual_attack(6, 40)

        if self.raw_defense:
            self.base_defense = self._calculate_actual_stat(
                self.raw_defense,
                self.base_stars,
                self.max_level_from_stars(self.base_stars)
            )
            self.max_lvl_defense = self.actual_defense(6, 40)

        if self.is_awakened and self.awakens_from:
            self.bestiary_slug = self.awakens_from.bestiary_slug
        else:
            if self.awakens_to is not None:
                self.bestiary_slug = slugify(" ".join([str(self.com2us_id), self.element, self.name, self.awakens_to.name]))
            else:
                self.bestiary_slug = slugify(" ".join([str(self.com2us_id), self.element, self.name]))

        super(Monster, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name', 'element']

    def __str__(self):
        if self.is_awakened:
            return self.name
        else:
            return self.name + ' (' + self.element.capitalize() + ')'


class AwakenCost(ItemQuantity):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE, related_name='awaken_materials')


class AwakenBonusType(IntEnum):
    NONE = 0
    STAT_BONUS = 1
    NEW_SKILL = 2
    LEADER_SKILL = 3
    STRENGTHEN_SKILL = 4
    SECONDARY_AWAKENING = 6


class MonsterCraftCost(models.Model):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    craft = models.ForeignKey(CraftMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return '{} - qty. {}'.format(self.craft.name, self.quantity)


class Fusion(models.Model):
    product = models.OneToOneField('Monster', on_delete=models.CASCADE, related_name='fusion')
    cost = models.IntegerField()
    ingredients = models.ManyToManyField('Monster', related_name='fusion_ingredient_for')
    meta_order = models.IntegerField(db_index=True, default=0)

    def __str__(self):
        return str(self.product) + ' Fusion'

    class Meta:
        ordering = ['meta_order']

    def sub_fusion_available(self):
        return Fusion.objects.filter(product__in=self.ingredients.values_list('awakens_from__pk', flat=True)).exists()

    def total_awakening_cost(self, owned_ingredients=None):
        cost = {
            'magic': {
                'low': 0,
                'mid': 0,
                'high': 0,
            },
            'fire': {
                'low': 0,
                'mid': 0,
                'high': 0,
            },
            'water': {
                'low': 0,
                'mid': 0,
                'high': 0,
            },
            'wind': {
                'low': 0,
                'mid': 0,
                'high': 0,
            },
            'light': {
                'low': 0,
                'mid': 0,
                'high': 0,
            },
            'dark': {
                'low': 0,
                'mid': 0,
                'high': 0,
            },
        }

        if owned_ingredients:
            qs = self.ingredients.exclude(pk__in=[o.monster.pk for o in owned_ingredients])
        else:
            qs = self.ingredients.all()

        for ingredient in qs:
            if ingredient.awakens_from:
                cost['magic']['low'] += ingredient.awakens_from.awaken_mats_magic_low
                cost['magic']['mid'] += ingredient.awakens_from.awaken_mats_magic_mid
                cost['magic']['high'] += ingredient.awakens_from.awaken_mats_magic_high
                cost['fire']['low'] += ingredient.awakens_from.awaken_mats_fire_low
                cost['fire']['mid'] += ingredient.awakens_from.awaken_mats_fire_mid
                cost['fire']['high'] += ingredient.awakens_from.awaken_mats_fire_high
                cost['water']['low'] += ingredient.awakens_from.awaken_mats_water_low
                cost['water']['mid'] += ingredient.awakens_from.awaken_mats_water_mid
                cost['water']['high'] += ingredient.awakens_from.awaken_mats_water_high
                cost['wind']['low'] += ingredient.awakens_from.awaken_mats_wind_low
                cost['wind']['mid'] += ingredient.awakens_from.awaken_mats_wind_mid
                cost['wind']['high'] += ingredient.awakens_from.awaken_mats_wind_high
                cost['light']['low'] += ingredient.awakens_from.awaken_mats_light_low
                cost['light']['mid'] += ingredient.awakens_from.awaken_mats_light_mid
                cost['light']['high'] += ingredient.awakens_from.awaken_mats_light_high
                cost['dark']['low'] += ingredient.awakens_from.awaken_mats_dark_low
                cost['dark']['mid'] += ingredient.awakens_from.awaken_mats_dark_mid
                cost['dark']['high'] += ingredient.awakens_from.awaken_mats_dark_high

        return cost
