from collections import OrderedDict
from functools import partial
from math import floor, ceil
from operator import is_not

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.text import slugify


class Monster(models.Model):
    ELEMENT_PURE = 'pure'
    ELEMENT_FIRE = 'fire'
    ELEMENT_WIND = 'wind'
    ELEMENT_WATER = 'water'
    ELEMENT_LIGHT = 'light'
    ELEMENT_DARK = 'dark'

    TYPE_ATTACK = 'attack'
    TYPE_HP = 'hp'
    TYPE_SUPPORT = 'support'
    TYPE_DEFENSE = 'defense'
    TYPE_MATERIAL = 'material'
    TYPE_NONE = 'none'

    ELEMENT_CHOICES = (
        (ELEMENT_PURE, 'Pure'),
        (ELEMENT_FIRE, 'Fire'),
        (ELEMENT_WIND, 'Wind'),
        (ELEMENT_WATER, 'Water'),
        (ELEMENT_LIGHT, 'Light'),
        (ELEMENT_DARK, 'Dark'),
    )

    TYPE_CHOICES = (
        (TYPE_NONE, 'None'),
        (TYPE_ATTACK, 'Attack'),
        (TYPE_HP, 'HP'),
        (TYPE_SUPPORT, 'Support'),
        (TYPE_DEFENSE, 'Defense'),
        (TYPE_MATERIAL, 'Material'),
    )

    STAR_CHOICES = (
        (1, mark_safe('1<span class="glyphicon glyphicon-star"></span>')),
        (2, mark_safe('2<span class="glyphicon glyphicon-star"></span>')),
        (3, mark_safe('3<span class="glyphicon glyphicon-star"></span>')),
        (4, mark_safe('4<span class="glyphicon glyphicon-star"></span>')),
        (5, mark_safe('5<span class="glyphicon glyphicon-star"></span>')),
        (6, mark_safe('6<span class="glyphicon glyphicon-star"></span>')),
    )

    name = models.CharField(max_length=40)
    com2us_id = models.IntegerField(blank=True, null=True, help_text='ID given in game data files')
    family_id = models.IntegerField(blank=True, null=True, help_text='Identifier that matches same family monsters')
    image_filename = models.CharField(max_length=250, null=True, blank=True)
    element = models.CharField(max_length=6, choices=ELEMENT_CHOICES, default=ELEMENT_FIRE)
    archetype = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_ATTACK)
    base_stars = models.IntegerField(choices=STAR_CHOICES, help_text='Default stars a monster is summoned at')
    obtainable = models.BooleanField(default=True, help_text='Is available for players to acquire')
    can_awaken = models.BooleanField(default=True, help_text='Has an awakened form')
    is_awakened = models.BooleanField(default=False, help_text='Is the awakened form')
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

    def monster_family(self):
        should_be_shown = Q(obtainable=True) | Q(transforms_into__isnull=False)
        family = Monster.objects.filter(family_id=self.family_id).filter(should_be_shown).order_by('element', 'is_awakened')

        return [
            family.filter(element=Monster.ELEMENT_FIRE).first(),
            family.filter(element=Monster.ELEMENT_WATER).first(),
            family.filter(element=Monster.ELEMENT_WIND).first(),
            family.filter(element=Monster.ELEMENT_LIGHT).first(),
            family.filter(element=Monster.ELEMENT_DARK).first(),
        ]

    def all_skill_effects(self):
        return SkillEffect.objects.filter(pk__in=self.skills.exclude(skill_effect=None).values_list('skill_effect', flat=True))

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

        # Pull info from unawakened version of this monster. This copying of data is one directional only
        if self.awakens_from:
            # Copy awaken bonus from unawakened version
            if self.is_awakened and self.awakens_from.awaken_bonus:
                self.awaken_bonus = self.awakens_from.awaken_bonus

        super(Monster, self).save(*args, **kwargs)

        # Automatically set awakens from/to relationship if none exists
        if self.awakens_from and self.awakens_from.awakens_to is not self:
            self.awakens_from.awakens_to = self
            self.awakens_from.save()
        elif self.awakens_to and self.awakens_to.awakens_from is not self:
            self.awakens_to.awakens_from = self
            self.awakens_to.save()

    class Meta:
        ordering = ['name', 'element']

    def __str__(self):
        if self.is_awakened:
            return self.name
        else:
            return self.name + ' (' + self.element.capitalize() + ')'


class Skill(models.Model):
    name = models.CharField(max_length=40)
    com2us_id = models.IntegerField(blank=True, null=True, help_text='ID given in game data files')
    description = models.TextField()
    slot = models.IntegerField(default=1, help_text='Which button position the skill is in during battle')
    skill_effect = models.ManyToManyField('SkillEffect', blank=True)
    effect = models.ManyToManyField('SkillEffect', through='SkillEffectDetail', blank=True, related_name='effect', help_text='Detailed skill effect information')
    cooltime = models.IntegerField(null=True, blank=True, help_text='Number of turns until skill can be used again')
    hits = models.IntegerField(default=1, help_text='Number of times this skill hits an enemy')
    aoe = models.BooleanField(default=False, help_text='Skill affects all enemies or allies')
    passive = models.BooleanField(default=False, help_text='Skill activates automatically')
    max_level = models.IntegerField()
    level_progress_description = models.TextField(null=True, blank=True, help_text='Description of bonus each skill level')
    icon_filename = models.CharField(max_length=100, null=True, blank=True)
    multiplier_formula = models.TextField(null=True, blank=True, help_text='Parsed multiplier formula')
    multiplier_formula_raw = models.CharField(max_length=150, null=True, blank=True, help_text='Multiplier formula given in game data files')
    scaling_stats = models.ManyToManyField('ScalingStat', blank=True, help_text='Monster stats which this skill scales on')

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/skills/' + self.icon_filename))
        else:
            return 'No Image'

    def level_progress_description_list(self):
        return self.level_progress_description.splitlines()

    def __str__(self):
        if self.name:
            name = self.name
        else:
            name = ''

        if self.icon_filename:
            icon = ' - ' + self.icon_filename
        else:
            icon = ''

        if self.com2us_id:
            com2us_id = ' - ' + str(self.com2us_id)
        else:
            com2us_id = ''

        return name + com2us_id + icon

    class Meta:
        ordering = ['slot', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'


class LeaderSkill(models.Model):
    ATTRIBUTE_HP = 1
    ATTRIBUTE_ATK = 2
    ATTRIBUTE_DEF = 3
    ATTRIBUTE_SPD = 4
    ATTRIBUTE_CRIT_RATE = 5
    ATTRIBUTE_RESIST = 6
    ATTRIBUTE_ACCURACY = 7
    ATTRIBUTE_CRIT_DMG = 8

    ATTRIBUTE_CHOICES = (
        (ATTRIBUTE_HP, 'HP'),
        (ATTRIBUTE_ATK, 'Attack Power'),
        (ATTRIBUTE_DEF, 'Defense'),
        (ATTRIBUTE_SPD, 'Attack Speed'),
        (ATTRIBUTE_CRIT_RATE, 'Critical Rate'),
        (ATTRIBUTE_RESIST, 'Resistance'),
        (ATTRIBUTE_ACCURACY, 'Accuracy'),
        (ATTRIBUTE_CRIT_DMG, 'Critical DMG'),
    )

    AREA_GENERAL = 1
    AREA_DUNGEON = 2
    AREA_ELEMENT = 3
    AREA_ARENA = 4
    AREA_GUILD = 5

    AREA_CHOICES = (
        (AREA_GENERAL, 'General'),
        (AREA_DUNGEON, 'Dungeon'),
        (AREA_ELEMENT, 'Element'),
        (AREA_ARENA, 'Arena'),
        (AREA_GUILD, 'Guild'),
    )

    attribute = models.IntegerField(choices=ATTRIBUTE_CHOICES, help_text='Monster stat which is granted the bonus')
    amount = models.IntegerField(help_text='Amount of bonus granted')
    area = models.IntegerField(choices=AREA_CHOICES, default=AREA_GENERAL, help_text='Where this leader skill has an effect')
    element = models.CharField(max_length=6, null=True, blank=True, choices=Monster.ELEMENT_CHOICES, help_text='Element of monster which this leader skill applies to')

    def skill_string(self):
        if self.area == self.AREA_DUNGEON:
            condition = 'in the Dungeons '
        elif self.area == self.AREA_ARENA:
            condition = 'in the Arena '
        elif self.area == self.AREA_GUILD:
            condition = 'in Guild Content '
        elif self.area == self.AREA_ELEMENT:
            condition = 'with {} attribute '.format(self.get_element_display())
        else:
            condition = ''

        return "Increase the {0} of ally monsters {1}by {2}%".format(self.get_attribute_display(), condition, self.amount)

    def icon_filename(self):
        if self.area == self.AREA_ELEMENT:
            suffix = '_{}'.format(self.get_element_display())
        elif self.area == self.AREA_GENERAL:
            suffix = ''
        else:
            suffix = '_{}'.format(self.get_area_display())

        return 'leader_skill_{0}{1}.png'.format(self.get_attribute_display().replace(' ', '_'), suffix)

    def image_url(self):
        return mark_safe('<img src="{}" height="42" width="42"/>'.format(
            static('herders/images/skills/leader/' + self.icon_filename())
        ))

    def __str__(self):
        if self.area == self.AREA_ELEMENT:
            condition = ' {}'.format(self.get_element_display())
        elif self.area == self.AREA_GENERAL:
            condition = ''
        else:
            condition = ' {}'.format(self.get_area_display())

        return self.get_attribute_display() + ' ' + str(self.amount) + '%' + condition

    class Meta:
        ordering = ['attribute', 'amount', 'element']
        verbose_name = 'Leader Skill'
        verbose_name_plural = 'Leader Skills'


class SkillEffectBuffsManager(models.Manager):
    def get_queryset(self):
        return super(SkillEffectBuffsManager, self).get_queryset().values_list('pk', 'icon_filename').filter(is_buff=True).exclude(icon_filename='')


class SkillEffectDebuffsManager(models.Manager):
    def get_queryset(self):
        return super(SkillEffectDebuffsManager, self).get_queryset().values_list('pk', 'icon_filename').filter(is_buff=False).exclude(icon_filename='')


class SkillEffectOtherManager(models.Manager):
    def get_queryset(self):
        return super(SkillEffectOtherManager, self).get_queryset().filter(icon_filename='')


class SkillEffect(models.Model):
    is_buff = models.BooleanField(default=True, help_text='Effect is beneficial to affected monster')
    name = models.CharField(max_length=40)
    description = models.TextField()
    icon_filename = models.CharField(max_length=100, blank=True, default='')

    objects = models.Manager()

    class Meta:
        ordering = ['name']
        verbose_name = 'Skill Effect'
        verbose_name_plural = 'Skill Effects'

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/buffs/' + self.icon_filename))
        else:
            return 'No Image'

    def __str__(self):
        return self.name


class SkillEffectDetail(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    effect = models.ForeignKey(SkillEffect, on_delete=models.CASCADE)
    aoe = models.BooleanField(default=False, help_text='Effect applies to entire friendly or enemy group')
    single_target = models.BooleanField(default=False, help_text='Effect applies to a single monster')
    self_effect = models.BooleanField(default=False, help_text='Effect applies to the monster using the skill')
    chance = models.IntegerField(null=True, blank=True, help_text='Chance of effect occuring per hit')
    on_crit = models.BooleanField(default=False)
    on_death = models.BooleanField(default=False)
    random = models.BooleanField(default=False, help_text='Skill effect applies randomly to the target')
    quantity = models.IntegerField(null=True, blank=True, help_text='Number of items this effect affects on the target')
    all = models.BooleanField(default=False, help_text='This effect affects all items on the target')
    self_hp = models.BooleanField(default=False, help_text="Amount of this effect is based on casting monster's HP")
    target_hp = models.BooleanField(default=False, help_text="Amount of this effect is based on target monster's HP")
    damage = models.BooleanField(default=False, help_text='Amount of this effect is based on damage dealt')
    note = models.TextField(blank=True, null=True, help_text="Explain anything else that doesn't fit in other fields")


class ScalingStat(models.Model):
    stat = models.CharField(max_length=20)
    com2us_desc = models.CharField(max_length=30, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.stat

    class Meta:
        ordering = ['stat',]
        verbose_name = 'Scaling Stat'
        verbose_name_plural = 'Scaling Stats'


class HomunculusSkill(models.Model):
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    monsters = models.ManyToManyField(Monster)
    craft_materials = models.ManyToManyField('CraftMaterial', through='HomunculusSkillCraftCost', help_text='Crafting materials required to purchase')
    mana_cost = models.IntegerField(default=0, help_text='Cost to purchase')
    prerequisites = models.ManyToManyField(Skill, blank=True, related_name='homunculus_prereq', help_text='Skills which must be acquired first')

    def __str__(self):
        return '{} ({})'.format(self.skill, self.skill.com2us_id)


class Source(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    icon_filename = models.CharField(max_length=100, null=True, blank=True)
    farmable_source = models.BooleanField(default=False)
    meta_order = models.IntegerField(db_index=True, default=0)

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/icons/' + self.icon_filename))
        else:
            return 'No Image'

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['meta_order', 'icon_filename', 'name']


class Fusion(models.Model):
    product = models.ForeignKey('Monster', on_delete=models.CASCADE, related_name='product')
    stars = models.IntegerField()
    cost = models.IntegerField()
    ingredients = models.ManyToManyField('Monster')
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


class Building(models.Model):
    AREA_GENERAL = 0
    AREA_GUILD = 1

    AREA_CHOICES = [
        (AREA_GENERAL, 'Everywhere'),
        (AREA_GUILD, 'Guild Content'),
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

    com2us_id = models.IntegerField()
    name = models.CharField(max_length=30)
    max_level = models.IntegerField()
    area = models.IntegerField(choices=AREA_CHOICES, null=True, blank=True)
    affected_stat = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    element = models.CharField(max_length=6, choices=Monster.ELEMENT_CHOICES, blank=True, null=True)
    stat_bonus = ArrayField(models.IntegerField(blank=True, null=True))
    upgrade_cost = ArrayField(models.IntegerField(blank=True, null=True))
    description = models.TextField(null=True, blank=True)
    icon_filename = models.CharField(max_length=100, null=True, blank=True)

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/buildings/' + self.icon_filename))
        else:
            return 'No Image'

    def __str__(self):
        return self.name


class CraftMaterial(models.Model):
    com2us_id = models.IntegerField()
    name = models.CharField(max_length=40)
    icon_filename = models.CharField(max_length=100, null=True, blank=True)
    sell_value = models.IntegerField(blank=True, null=True)
    source = models.ManyToManyField(Source, blank=True)

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/crafts/' + self.icon_filename))
        else:
            return 'No Image'

    def __str__(self):
        return self.name


class MonsterCraftCost(models.Model):
    monster = models.ForeignKey(Monster, on_delete=models.CASCADE)
    craft = models.ForeignKey(CraftMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return '{} - qty. {}'.format(self.craft.name, self.quantity)


class HomunculusSkillCraftCost(models.Model):
    skill = models.ForeignKey(HomunculusSkill, on_delete=models.CASCADE)
    craft = models.ForeignKey(CraftMaterial, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return '{} - qty. {}'.format(self.craft.name, self.quantity)


class RuneObjectBase:
    # Provides basic rune related constants
    TYPE_ENERGY = 1
    TYPE_FATAL = 2
    TYPE_BLADE = 3
    TYPE_RAGE = 4
    TYPE_SWIFT = 5
    TYPE_FOCUS = 6
    TYPE_GUARD = 7
    TYPE_ENDURE = 8
    TYPE_VIOLENT = 9
    TYPE_WILL = 10
    TYPE_NEMESIS = 11
    TYPE_SHIELD = 12
    TYPE_REVENGE = 13
    TYPE_DESPAIR = 14
    TYPE_VAMPIRE = 15
    TYPE_DESTROY = 16
    TYPE_FIGHT = 17
    TYPE_DETERMINATION = 18
    TYPE_ENHANCE = 19
    TYPE_ACCURACY = 20
    TYPE_TOLERANCE = 21

    TYPE_CHOICES = (
        (TYPE_ENERGY, 'Energy'),
        (TYPE_FATAL, 'Fatal'),
        (TYPE_BLADE, 'Blade'),
        (TYPE_RAGE, 'Rage'),
        (TYPE_SWIFT, 'Swift'),
        (TYPE_FOCUS, 'Focus'),
        (TYPE_GUARD, 'Guard'),
        (TYPE_ENDURE, 'Endure'),
        (TYPE_VIOLENT, 'Violent'),
        (TYPE_WILL, 'Will'),
        (TYPE_NEMESIS, 'Nemesis'),
        (TYPE_SHIELD, 'Shield'),
        (TYPE_REVENGE, 'Revenge'),
        (TYPE_DESPAIR, 'Despair'),
        (TYPE_VAMPIRE, 'Vampire'),
        (TYPE_DESTROY, 'Destroy'),
        (TYPE_FIGHT, 'Fight'),
        (TYPE_DETERMINATION, 'Determination'),
        (TYPE_ENHANCE, 'Enhance'),
        (TYPE_ACCURACY, 'Accuracy'),
        (TYPE_TOLERANCE, 'Tolerance'),
    )

    STAR_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
    )

    STAT_HP = 1
    STAT_HP_PCT = 2
    STAT_ATK = 3
    STAT_ATK_PCT = 4
    STAT_DEF = 5
    STAT_DEF_PCT = 6
    STAT_SPD = 7
    STAT_CRIT_RATE_PCT = 8
    STAT_CRIT_DMG_PCT = 9
    STAT_RESIST_PCT = 10
    STAT_ACCURACY_PCT = 11

    # Used for selecting type of stat in form
    STAT_CHOICES = (
        (STAT_HP, 'HP'),
        (STAT_HP_PCT, 'HP %'),
        (STAT_ATK, 'ATK'),
        (STAT_ATK_PCT, 'ATK %'),
        (STAT_DEF, 'DEF'),
        (STAT_DEF_PCT, 'DEF %'),
        (STAT_SPD, 'SPD'),
        (STAT_CRIT_RATE_PCT, 'CRI Rate %'),
        (STAT_CRIT_DMG_PCT, 'CRI Dmg %'),
        (STAT_RESIST_PCT, 'Resistance %'),
        (STAT_ACCURACY_PCT, 'Accuracy %'),
    )

    # The STAT_DISPLAY is used to construct rune values for display as 'HP: 5%' rather than 'HP %: 5' using
    # the built in get_FOO_display() functions
    STAT_DISPLAY = {
        STAT_HP: 'HP',
        STAT_HP_PCT: 'HP',
        STAT_ATK: 'ATK',
        STAT_ATK_PCT: 'ATK',
        STAT_DEF: 'DEF',
        STAT_DEF_PCT: 'DEF',
        STAT_SPD: 'SPD',
        STAT_CRIT_RATE_PCT: 'CRI Rate',
        STAT_CRIT_DMG_PCT: 'CRI Dmg',
        STAT_RESIST_PCT: 'Resistance',
        STAT_ACCURACY_PCT: 'Accuracy',
    }

    PERCENT_STATS = [
        STAT_HP_PCT,
        STAT_ATK_PCT,
        STAT_DEF_PCT,
        STAT_CRIT_RATE_PCT,
        STAT_CRIT_DMG_PCT,
        STAT_RESIST_PCT,
        STAT_ACCURACY_PCT,
    ]

    FLAT_STATS = [
        STAT_HP,
        STAT_ATK,
        STAT_DEF,
        STAT_SPD,
    ]

    QUALITY_NORMAL = 0
    QUALITY_MAGIC = 1
    QUALITY_RARE = 2
    QUALITY_HERO = 3
    QUALITY_LEGEND = 4

    QUALITY_CHOICES = (
        (QUALITY_NORMAL, 'Normal'),
        (QUALITY_MAGIC, 'Magic'),
        (QUALITY_RARE, 'Rare'),
        (QUALITY_HERO, 'Hero'),
        (QUALITY_LEGEND, 'Legend'),
    )


class Rune(models.Model, RuneObjectBase):
    MAIN_STAT_VALUES = {
        # [stat][stars][level]: value
        RuneObjectBase.STAT_HP: {
            1: [40, 85, 130, 175, 220, 265, 310, 355, 400, 445, 490, 535, 580, 625, 670, 804],
            2: [70, 130, 190, 250, 310, 370, 430, 490, 550, 610, 670, 730, 790, 850, 910, 1092],
            3: [100, 175, 250, 325, 400, 475, 550, 625, 700, 775, 850, 925, 1000, 1075, 1150, 1380],
            4: [160, 250, 340, 430, 520, 610, 700, 790, 880, 970, 1060, 1150, 1240, 1330, 1420, 1704],
            5: [270, 375, 480, 585, 690, 795, 900, 1005, 1110, 1215, 1320, 1425, 1530, 1635, 1740, 2088],
            6: [360, 480, 600, 720, 840, 960, 1080, 1200, 1320, 1440, 1560, 1680, 1800, 1920, 2040, 2448],
        },
        RuneObjectBase.STAT_HP_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        RuneObjectBase.STAT_ATK: {
            1: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
            2: [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
            3: [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
            4: [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
            5: [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
            6: [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160],
        },
        RuneObjectBase.STAT_ATK_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        RuneObjectBase.STAT_DEF: {
            1: [3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 54],
            2: [5, 9, 13, 17, 21, 25, 29, 33, 37, 41, 45, 49, 53, 57, 61, 73],
            3: [7, 12, 17, 22, 27, 32, 37, 42, 47, 52, 57, 62, 67, 72, 77, 92],
            4: [10, 16, 22, 28, 34, 40, 46, 52, 58, 64, 70, 76, 82, 88, 94, 112],
            5: [15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 135],
            6: [22, 30, 38, 46, 54, 62, 70, 78, 86, 94, 102, 110, 118, 126, 134, 160],
        },
        RuneObjectBase.STAT_DEF_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [5, 7, 9, 11, 13, 16, 18, 20, 22, 24, 27, 29, 31, 33, 36, 43],
            5: [8, 10, 12, 15, 17, 20, 22, 24, 27, 29, 32, 34, 37, 40, 43, 51],
            6: [11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 63],
        },
        RuneObjectBase.STAT_SPD: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 16, 17, 18, 19, 21, 25],
            4: [4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 20, 22, 23, 25, 30],
            5: [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 39],
            6: [7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 33, 35, 42],
        },
        RuneObjectBase.STAT_CRIT_RATE_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
            4: [4, 6, 8, 11, 13, 15, 17, 19, 22, 24, 26, 28, 30, 33, 35, 41],
            5: [5, 7, 10, 12, 15, 17, 19, 22, 24, 27, 29, 31, 34, 36, 39, 47],
            6: [7, 10, 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 58],
        },
        RuneObjectBase.STAT_CRIT_DMG_PCT: {
            1: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            2: [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31, 37],
            3: [4, 6, 9, 11, 13, 16, 18, 20, 22, 25, 27, 29, 32, 34, 36, 43],
            4: [6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 57],
            5: [8, 11, 15, 18, 21, 25, 28, 31, 34, 38, 41, 44, 48, 51, 54, 65],
            6: [11, 15, 19, 23, 27, 31, 35, 39, 43, 47, 51, 55, 59, 63, 67, 80],
        },
        RuneObjectBase.STAT_RESIST_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
            5: [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
            6: [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64],
        },
        RuneObjectBase.STAT_ACCURACY_PCT: {
            1: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 18],
            2: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19],
            3: [4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 38],
            4: [6, 8, 10, 13, 15, 17, 19, 21, 24, 26, 28, 30, 32, 35, 37, 44],
            5: [9, 11, 14, 16, 19, 21, 23, 26, 28, 31, 33, 35, 38, 40, 43, 51],
            6: [12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51, 54, 64],
        },
    }

    MAIN_STATS_BY_SLOT = {
        1: [
            RuneObjectBase.STAT_ATK,
        ],
        2: [
            RuneObjectBase.STAT_ATK,
            RuneObjectBase.STAT_ATK_PCT,
            RuneObjectBase.STAT_DEF,
            RuneObjectBase.STAT_DEF_PCT,
            RuneObjectBase.STAT_HP,
            RuneObjectBase.STAT_HP_PCT,
            RuneObjectBase.STAT_SPD,
        ],
        3: [
            RuneObjectBase.STAT_DEF,
        ],
        4: [
            RuneObjectBase.STAT_ATK,
            RuneObjectBase.STAT_ATK_PCT,
            RuneObjectBase.STAT_DEF,
            RuneObjectBase.STAT_DEF_PCT,
            RuneObjectBase.STAT_HP,
            RuneObjectBase.STAT_HP_PCT,
            RuneObjectBase.STAT_CRIT_RATE_PCT,
            RuneObjectBase.STAT_CRIT_DMG_PCT,
        ],
        5: [
            RuneObjectBase.STAT_HP,
        ],
        6: [
            RuneObjectBase.STAT_ATK,
            RuneObjectBase.STAT_ATK_PCT,
            RuneObjectBase.STAT_DEF,
            RuneObjectBase.STAT_DEF_PCT,
            RuneObjectBase.STAT_HP,
            RuneObjectBase.STAT_HP_PCT,
            RuneObjectBase.STAT_RESIST_PCT,
            RuneObjectBase.STAT_ACCURACY_PCT,
        ]
    }

    SUBSTAT_INCREMENTS = {
        # [stat][stars]: value
        RuneObjectBase.STAT_HP: {
            1: 60,
            2: 105,
            3: 165,
            4: 225,
            5: 300,
            6: 375,
        },
        RuneObjectBase.STAT_HP_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_ATK: {
            1: 4,
            2: 5,
            3: 8,
            4: 10,
            5: 15,
            6: 20,
        },
        RuneObjectBase.STAT_ATK_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_DEF: {
            1: 4,
            2: 5,
            3: 8,
            4: 10,
            5: 15,
            6: 20,
        },
        RuneObjectBase.STAT_DEF_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_SPD: {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
        },
        RuneObjectBase.STAT_CRIT_RATE_PCT: {
            1: 1,
            2: 2,
            3: 3,
            4: 4,
            5: 5,
            6: 6,
        },
        RuneObjectBase.STAT_CRIT_DMG_PCT: {
            1: 2,
            2: 3,
            3: 4,
            4: 5,
            5: 6,
            6: 7,
        },
        RuneObjectBase.STAT_RESIST_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
        RuneObjectBase.STAT_ACCURACY_PCT: {
            1: 2,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 8,
        },
    }

    INNATE_STAT_TITLES = {
        RuneObjectBase.STAT_HP: 'Strong',
        RuneObjectBase.STAT_HP_PCT: 'Tenacious',
        RuneObjectBase.STAT_ATK: 'Ferocious',
        RuneObjectBase.STAT_ATK_PCT: 'Powerful',
        RuneObjectBase.STAT_DEF: 'Sturdy',
        RuneObjectBase.STAT_DEF_PCT: 'Durable',
        RuneObjectBase.STAT_SPD: 'Quick',
        RuneObjectBase.STAT_CRIT_RATE_PCT: 'Mortal',
        RuneObjectBase.STAT_CRIT_DMG_PCT: 'Cruel',
        RuneObjectBase.STAT_RESIST_PCT: 'Resistant',
        RuneObjectBase.STAT_ACCURACY_PCT: 'Intricate',
    }

    RUNE_SET_COUNT_REQUIREMENTS = {
        RuneObjectBase.TYPE_ENERGY: 2,
        RuneObjectBase.TYPE_FATAL: 4,
        RuneObjectBase.TYPE_BLADE: 2,
        RuneObjectBase.TYPE_RAGE: 4,
        RuneObjectBase.TYPE_SWIFT: 4,
        RuneObjectBase.TYPE_FOCUS: 2,
        RuneObjectBase.TYPE_GUARD: 2,
        RuneObjectBase.TYPE_ENDURE: 2,
        RuneObjectBase.TYPE_VIOLENT: 4,
        RuneObjectBase.TYPE_WILL: 2,
        RuneObjectBase.TYPE_NEMESIS: 2,
        RuneObjectBase.TYPE_SHIELD: 2,
        RuneObjectBase.TYPE_REVENGE: 2,
        RuneObjectBase.TYPE_DESPAIR: 4,
        RuneObjectBase.TYPE_VAMPIRE: 4,
        RuneObjectBase.TYPE_DESTROY: 2,
        RuneObjectBase.TYPE_FIGHT: 2,
        RuneObjectBase.TYPE_DETERMINATION: 2,
        RuneObjectBase.TYPE_ENHANCE: 2,
        RuneObjectBase.TYPE_ACCURACY: 2,
        RuneObjectBase.TYPE_TOLERANCE: 2,
    }

    RUNE_SET_BONUSES = {
        RuneObjectBase.TYPE_ENERGY: {
            'count': 2,
            'stat': RuneObjectBase.STAT_HP_PCT,
            'value': 15.0,
            'team': False,
            'description': '2 Set: HP +15%',
        },
        RuneObjectBase.TYPE_FATAL: {
            'count': 4,
            'stat': RuneObjectBase.STAT_ATK_PCT,
            'value': 35.0,
            'team': False,
            'description': '4 Set: Attack Power +35%',
        },
        RuneObjectBase.TYPE_BLADE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_CRIT_RATE_PCT,
            'value': 12.0,
            'team': False,
            'description': '2 Set: Critical Rate +12%',
        },
        RuneObjectBase.TYPE_RAGE: {
            'count': 4,
            'stat': RuneObjectBase.STAT_CRIT_DMG_PCT,
            'value': 40.0,
            'team': False,
            'description': '4 Set: Critical Damage +40%',
        },
        RuneObjectBase.TYPE_SWIFT: {
            'count': 4,
            'stat': RuneObjectBase.STAT_SPD,
            'value': 25.0,
            'team': False,
            'description': '4 Set: Attack Speed +25%',
        },
        RuneObjectBase.TYPE_FOCUS: {
            'count': 2,
            'stat': RuneObjectBase.STAT_ACCURACY_PCT,
            'value': 20.0,
            'team': False,
            'description': '2 Set: Accuracy +20%',
        },
        RuneObjectBase.TYPE_GUARD: {
            'count': 2,
            'stat': RuneObjectBase.STAT_DEF_PCT,
            'value': 15.0,
            'team': False,
            'description': '2 Set: Defense +15%',
        },
        RuneObjectBase.TYPE_ENDURE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_RESIST_PCT,
            'value': 20.0,
            'team': False,
            'description': '2 Set: Resistance +20%',
        },
        RuneObjectBase.TYPE_VIOLENT: {
            'count': 4,
            'stat': None,
            'value': None,
            'team': False,
            'description': '4 Set: Get Extra Turn +22%',
        },
        RuneObjectBase.TYPE_WILL: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': '2 Set: Immunity +1 turn',
        },
        RuneObjectBase.TYPE_NEMESIS: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': '2 Set: ATK Gauge +4% (for every 7% HP lost)',
        },
        RuneObjectBase.TYPE_SHIELD: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': True,
            'description': '2 Set: Ally Shield 3 turns (15% of HP)',
        },
        RuneObjectBase.TYPE_REVENGE: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': '2 Set: Counterattack +15%',
        },
        RuneObjectBase.TYPE_DESPAIR: {
            'count': 4,
            'stat': None,
            'value': None,
            'team': False,
            'description': '4 Set: Stun Rate +25%',
        },
        RuneObjectBase.TYPE_VAMPIRE: {
            'count': 4,
            'stat': None,
            'value': None,
            'team': False,
            'description': '4 Set: Life Drain +35%',
        },
        RuneObjectBase.TYPE_DESTROY: {
            'count': 2,
            'stat': None,
            'value': None,
            'team': False,
            'description': "2 Set: 30% of the damage dealt will reduce up to 4% of the enemy's Max HP",
        },
        RuneObjectBase.TYPE_FIGHT: {
            'count': 2,
            'stat': RuneObjectBase.STAT_ATK,
            'value': 7.0,
            'team': True,
            'description': '2 Set: Increase the Attack Power of all allies by 7%',
        },
        RuneObjectBase.TYPE_DETERMINATION: {
            'count': 2,
            'stat': RuneObjectBase.STAT_DEF,
            'value': 7.0,
            'team': True,
            'description': '2 Set: Increase the Defense of all allies by 7%',
        },
        RuneObjectBase.TYPE_ENHANCE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_HP,
            'value': 7.0,
            'team': True,
            'description': '2 Set: Increase the HP of all allies by 7%',
        },
        RuneObjectBase.TYPE_ACCURACY: {
            'count': 2,
            'stat': RuneObjectBase.STAT_ACCURACY_PCT,
            'value': 10.0,
            'team': True,
            'description': '2 Set: Increase the Accuracy of all allies by 10%',
        },
        RuneObjectBase.TYPE_TOLERANCE: {
            'count': 2,
            'stat': RuneObjectBase.STAT_RESIST_PCT,
            'value': 10.0,
            'team': True,
            'description': '2 Set: Increase the Resistance of all allies by 10%',
        },
    }

    type = models.IntegerField(choices=RuneObjectBase.TYPE_CHOICES)
    stars = models.IntegerField()
    level = models.IntegerField()
    slot = models.IntegerField()
    quality = models.IntegerField(default=0, choices=RuneObjectBase.QUALITY_CHOICES)
    original_quality = models.IntegerField(choices=RuneObjectBase.QUALITY_CHOICES, blank=True, null=True)
    value = models.IntegerField(blank=True, null=True)
    main_stat = models.IntegerField(choices=RuneObjectBase.STAT_CHOICES)
    main_stat_value = models.IntegerField()
    innate_stat = models.IntegerField(choices=RuneObjectBase.STAT_CHOICES, null=True, blank=True)
    innate_stat_value = models.IntegerField(null=True, blank=True)
    substats = ArrayField(
        models.IntegerField(choices=RuneObjectBase.STAT_CHOICES, null=True, blank=True),
        size=4,
        default=list,
    )
    substat_values = ArrayField(
        models.IntegerField(blank=True, null=True),
        size=4,
        default=list,
    )

    # The following fields exist purely to allow easier filtering and are updated on model save
    has_hp = models.BooleanField(default=False)
    has_atk = models.BooleanField(default=False)
    has_def = models.BooleanField(default=False)
    has_crit_rate = models.BooleanField(default=False)
    has_crit_dmg = models.BooleanField(default=False)
    has_speed = models.BooleanField(default=False)
    has_resist = models.BooleanField(default=False)
    has_accuracy = models.BooleanField(default=False)
    efficiency = models.FloatField(blank=True, null=True)
    max_efficiency = models.FloatField(blank=True, null=True)
    substat_upgrades_remaining = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    def get_main_stat_rune_display(self):
        return RuneObjectBase.STAT_DISPLAY.get(self.main_stat, '')

    def get_innate_stat_rune_display(self):
        return RuneObjectBase.STAT_DISPLAY.get(self.innate_stat, '')

    def get_substat_rune_display(self, idx):
        if len(self.substats) > idx:
            return RuneObjectBase.STAT_DISPLAY.get(self.substats[idx], '')
        else:
            return ''

    def get_stat(self, stat_type, sub_stats_only=False):
        if self.main_stat == stat_type and not sub_stats_only:
            return self.main_stat_value
        elif self.innate_stat == stat_type and not sub_stats_only:
            return self.innate_stat_value
        else:
            for idx, substat in enumerate(self.substats):
                if substat == stat_type:
                    return self.substat_values[idx]

        return 0

    @property
    def substat_upgrades_received(self):
        return int(floor(min(self.level, 12) / 3) + 1)

    def get_efficiency(self):
        # https://www.youtube.com/watch?v=SBWeptNNbYc
        # All runes are compared against max stat values for perfect 6* runes.

        # Main stat efficiency
        running_sum = float(self.MAIN_STAT_VALUES[self.main_stat][self.stars][15]) / float(self.MAIN_STAT_VALUES[self.main_stat][6][15])

        # Substat efficiencies
        if self.innate_stat is not None:
            running_sum += self.innate_stat_value / float(self.SUBSTAT_INCREMENTS[self.innate_stat][6] * 5)

        for substat, value in zip(self.substats, self.substat_values):
            running_sum += value / float(self.SUBSTAT_INCREMENTS[substat][6] * 5)

        return running_sum / 2.8 * 100

    def update_fields(self):
        # Set filterable fields
        rune_stat_types = [self.main_stat, self.innate_stat] + self.substats
        self.has_hp = any([i for i in rune_stat_types if i in [self.STAT_HP, self.STAT_HP_PCT]])
        self.has_atk = any([i for i in rune_stat_types if i in [self.STAT_ATK, self.STAT_ATK_PCT]])
        self.has_def = any([i for i in rune_stat_types if i in [self.STAT_DEF, self.STAT_DEF_PCT]])
        self.has_crit_rate = self.STAT_CRIT_RATE_PCT in rune_stat_types
        self.has_crit_dmg = self.STAT_CRIT_DMG_PCT in rune_stat_types
        self.has_speed = self.STAT_SPD in rune_stat_types
        self.has_resist = self.STAT_RESIST_PCT in rune_stat_types
        self.has_accuracy = self.STAT_ACCURACY_PCT in rune_stat_types

        self.quality = len([substat for substat in self.substats if substat])
        self.substat_upgrades_remaining = 5 - self.substat_upgrades_received
        self.efficiency = self.get_efficiency()
        self.max_efficiency = self.efficiency + max(ceil((12 - self.level) / 3.0), 0) * 0.2 / 2.8 * 100

        # Cap stat values to appropriate value
        # Very old runes can have different values, but never higher than the cap
        if self.main_stat_value:
            self.main_stat_value = min(self.MAIN_STAT_VALUES[self.main_stat][self.stars][15], self.main_stat_value)
        else:
            self.main_stat_value = self.MAIN_STAT_VALUES[self.main_stat][self.stars][self.level]

        if self.innate_stat and self.innate_stat_value > self.SUBSTAT_INCREMENTS[self.innate_stat][self.stars]:
            self.innate_stat_value = self.SUBSTAT_INCREMENTS[self.innate_stat][self.stars]

        for idx, substat in enumerate(self.substats):
            max_sub_value = self.SUBSTAT_INCREMENTS[substat][self.stars] * self.substat_upgrades_received
            if self.substat_values[idx] > max_sub_value:
                self.substat_values[idx] = max_sub_value

    def clean(self):
        # Check slot, level, etc for valid ranges
        if self.level is None or self.level < 0 or self.level > 15:
            raise ValidationError({
                'level': ValidationError(
                    'Level must be 0 through 15.',
                    code='invalid_rune_level',
                )
            })

        if self.stars is None or (self.stars < 1 or self.stars > 6):
            raise ValidationError({
                'stars': ValidationError(
                    'Stars must be between 1 and 6.',
                    code='invalid_rune_stars',
                )
            })

        if self.slot is not None:
            if self.slot < 1 or self.slot > 6:
                raise ValidationError({
                    'slot': ValidationError(
                        'Slot must be 1 through 6.',
                        code='invalid_rune_slot',
                    )
                })
            # Do slot vs stat check
            if self.main_stat not in self.MAIN_STATS_BY_SLOT[self.slot]:
                raise ValidationError({
                    'main_stat': ValidationError(
                        'Unacceptable stat for slot %(slot)s. Must be %(valid_stats)s.',
                        params={
                            'slot': self.slot,
                            'valid_stats': ', '.join([RuneObjectBase.STAT_CHOICES[stat - 1][1] for stat in self.MAIN_STATS_BY_SLOT[self.slot]])
                        },
                        code='invalid_rune_main_stat'
                    ),
                })

        # Check that the same stat type was not used multiple times
        stat_list = list(filter(
            partial(is_not, None),
            [self.main_stat, self.innate_stat] + self.substats
        ))
        if len(stat_list) != len(set(stat_list)):
            raise ValidationError(
                'All stats and substats must be unique.',
                code='duplicate_stats'
            )

        # Check if stat type was specified that it has value > 0
        if self.main_stat_value is None:
            raise ValidationError({
                'main_stat_value': ValidationError(
                    'Missing main stat value.',
                    code='main_stat_missing_value',
                )
            })

        max_main_stat_value = self.MAIN_STAT_VALUES[self.main_stat][self.stars][self.level]
        if self.main_stat_value > max_main_stat_value:
            raise ValidationError(
                f'Main stat value for {self.get_main_stat_display()} at {self.stars}* lv. {self.level} must be less than {max_main_stat_value}',
                code='main_stat_value_invalid',
            )

        if self.innate_stat is not None:
            if self.innate_stat_value is None or self.innate_stat_value <= 0:
                raise ValidationError({
                    'innate_stat_value': ValidationError(
                        'Must be greater than 0.',
                        code='invalid_rune_innate_stat_value'
                    )
                })
            max_sub_value = self.SUBSTAT_INCREMENTS[self.innate_stat][self.stars]
            if self.innate_stat_value > max_sub_value:
                raise ValidationError({
                    'innate_stat_value': ValidationError(
                        'Must be less than or equal to ' + str(max_sub_value) + '.',
                        code='invalid_rune_innate_stat_value'
                    )
                })

        for substat, value in zip(self.substats, self.substat_values):
            if value is None or value <= 0:
                raise ValidationError({
                    f'substat_values]': ValidationError(
                        'Must be greater than 0.',
                        code=f'invalid_rune_substat_values'
                    )
                })

            max_sub_value = self.SUBSTAT_INCREMENTS[substat][self.stars] * self.substat_upgrades_received
            if value > max_sub_value:
                raise ValidationError({
                    f'substat_values': ValidationError(
                        'Must be less than or equal to ' + str(max_sub_value) + '.',
                        code=f'invalid_rune_substat_value]'
                    )
                })


class RuneCraft(RuneObjectBase):
    CRAFT_GRINDSTONE = 0
    CRAFT_ENCHANT_GEM = 1
    CRAFT_IMMEMORIAL_GRINDSTONE = 2
    CRAFT_IMMEMORIAL_GEM = 3

    CRAFT_CHOICES = (
        (CRAFT_GRINDSTONE, 'Grindstone'),
        (CRAFT_ENCHANT_GEM, 'Enchant Gem'),
        (CRAFT_IMMEMORIAL_GRINDSTONE, 'Immemorial Grindstone'),
        (CRAFT_IMMEMORIAL_GEM, 'Immemorial Gem'),
    )

    CRAFT_ENCHANT_GEMS = [
        CRAFT_ENCHANT_GEM,
        CRAFT_IMMEMORIAL_GEM,
    ]

    CRAFT_GRINDSTONES = [
        CRAFT_GRINDSTONE,
        CRAFT_IMMEMORIAL_GRINDSTONE,
    ]

    # Type > Stat > Quality > Min/Max
    CRAFT_VALUE_RANGES = {
        CRAFT_GRINDSTONE: {
            RuneObjectBase.STAT_HP: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 80, 'max': 120},
                RuneObjectBase.QUALITY_MAGIC: {'min': 100, 'max': 200},
                RuneObjectBase.QUALITY_RARE: {'min': 180, 'max': 250},
                RuneObjectBase.QUALITY_HERO: {'min': 230, 'max': 450},
                RuneObjectBase.QUALITY_LEGEND: {'min': 430, 'max': 550},
            },
            RuneObjectBase.STAT_HP_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneObjectBase.STAT_ATK: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 4, 'max': 8},
                RuneObjectBase.QUALITY_MAGIC: {'min': 6, 'max': 12},
                RuneObjectBase.QUALITY_RARE: {'min': 10, 'max': 18},
                RuneObjectBase.QUALITY_HERO: {'min': 12, 'max': 22},
                RuneObjectBase.QUALITY_LEGEND: {'min': 18, 'max': 30},
            },
            RuneObjectBase.STAT_ATK_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneObjectBase.STAT_DEF: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 4, 'max': 8},
                RuneObjectBase.QUALITY_MAGIC: {'min': 6, 'max': 12},
                RuneObjectBase.QUALITY_RARE: {'min': 10, 'max': 18},
                RuneObjectBase.QUALITY_HERO: {'min': 12, 'max': 22},
                RuneObjectBase.QUALITY_LEGEND: {'min': 18, 'max': 30},
            },
            RuneObjectBase.STAT_DEF_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 10},
            },
            RuneObjectBase.STAT_SPD: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 2},
                RuneObjectBase.QUALITY_MAGIC: {'min': 1, 'max': 2},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 3},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 4},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 5},
            },
            RuneObjectBase.STAT_CRIT_RATE_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 2},
                RuneObjectBase.QUALITY_MAGIC: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
            },
            RuneObjectBase.STAT_CRIT_DMG_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 7},
            },
            RuneObjectBase.STAT_RESIST_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
            RuneObjectBase.STAT_ACCURACY_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 2, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 8},
            },
        },
        CRAFT_ENCHANT_GEM: {
            RuneObjectBase.STAT_HP: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 100, 'max': 150},
                RuneObjectBase.QUALITY_MAGIC: {'min': 130, 'max': 220},
                RuneObjectBase.QUALITY_RARE: {'min': 200, 'max': 310},
                RuneObjectBase.QUALITY_HERO: {'min': 290, 'max': 420},
                RuneObjectBase.QUALITY_LEGEND: {'min': 400, 'max': 580},
            },
            RuneObjectBase.STAT_HP_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneObjectBase.STAT_ATK: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 8, 'max': 12},
                RuneObjectBase.QUALITY_MAGIC: {'min': 10, 'max': 16},
                RuneObjectBase.QUALITY_RARE: {'min': 15, 'max': 23},
                RuneObjectBase.QUALITY_HERO: {'min': 20, 'max': 30},
                RuneObjectBase.QUALITY_LEGEND: {'min': 28, 'max': 40},
            },
            RuneObjectBase.STAT_ATK_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneObjectBase.STAT_DEF: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 8, 'max': 12},
                RuneObjectBase.QUALITY_MAGIC: {'min': 10, 'max': 16},
                RuneObjectBase.QUALITY_RARE: {'min': 15, 'max': 23},
                RuneObjectBase.QUALITY_HERO: {'min': 20, 'max': 30},
                RuneObjectBase.QUALITY_LEGEND: {'min': 28, 'max': 40},
            },
            RuneObjectBase.STAT_DEF_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 7},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 9},
                RuneObjectBase.QUALITY_HERO: {'min': 7, 'max': 11},
                RuneObjectBase.QUALITY_LEGEND: {'min': 9, 'max': 13},
            },
            RuneObjectBase.STAT_SPD: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 10},
            },
            RuneObjectBase.STAT_CRIT_RATE_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 1, 'max': 3},
                RuneObjectBase.QUALITY_MAGIC: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_RARE: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_HERO: {'min': 4, 'max': 7},
                RuneObjectBase.QUALITY_LEGEND: {'min': 6, 'max': 9},
            },
            RuneObjectBase.STAT_CRIT_DMG_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 5},
                RuneObjectBase.QUALITY_RARE: {'min': 4, 'max': 6},
                RuneObjectBase.QUALITY_HERO: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 10},
            },
            RuneObjectBase.STAT_RESIST_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 6, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 8, 'max': 11},
            },
            RuneObjectBase.STAT_ACCURACY_PCT: {
                RuneObjectBase.QUALITY_NORMAL: {'min': 2, 'max': 4},
                RuneObjectBase.QUALITY_MAGIC: {'min': 3, 'max': 6},
                RuneObjectBase.QUALITY_RARE: {'min': 5, 'max': 8},
                RuneObjectBase.QUALITY_HERO: {'min': 6, 'max': 9},
                RuneObjectBase.QUALITY_LEGEND: {'min': 8, 'max': 11},
            },
        }
    }
    CRAFT_VALUE_RANGES[CRAFT_IMMEMORIAL_GEM] = CRAFT_VALUE_RANGES[CRAFT_ENCHANT_GEM]
    CRAFT_VALUE_RANGES[CRAFT_IMMEMORIAL_GRINDSTONE] = CRAFT_VALUE_RANGES[CRAFT_GRINDSTONE]


class Dungeon(models.Model):
    CATEGORY_SCENARIO = 0
    CATEGORY_RUNE_DUNGEON = 1
    CATEGORY_ESSENCE_DUNGEON = 2
    CATEGORY_OTHER_DUNGEON = 3
    CATEGORY_RIFT_OF_WORLDS_RAID = 4
    CATEGORY_HALL_OF_HEROES = 5
    CATEGORY_RIFT_OF_WORLDS_BEASTS = 6

    CATEGORY_CHOICES = [
        (CATEGORY_SCENARIO, 'Scenarios'),
        (CATEGORY_RUNE_DUNGEON, 'Rune Dungeons'),
        (CATEGORY_ESSENCE_DUNGEON, 'Elemental Dungeons'),
        (CATEGORY_OTHER_DUNGEON, 'Other Dungeons'),
        (CATEGORY_RIFT_OF_WORLDS_RAID, 'Rift Raid'),
        (CATEGORY_RIFT_OF_WORLDS_BEASTS, 'Rift Beast'),
        (CATEGORY_HALL_OF_HEROES, 'Hall of Heroes'),
    ]

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(blank=True, null=True)
    category = models.IntegerField(choices=CATEGORY_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Dungeon, self).save(*args, **kwargs)


class Scenario(Dungeon):
    DIFFICULTY_NORMAL = 1
    DIFFICULTY_HARD = 2
    DIFFICULTY_HELL = 3
    DIFFICULTY_CHOICES = (
        (DIFFICULTY_NORMAL, 'Normal'),
        (DIFFICULTY_HARD, 'Hard'),
        (DIFFICULTY_HELL, 'Hell'),
    )

    stage = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=DIFFICULTY_NORMAL)
    energy_cost = models.IntegerField(default=0, help_text='Energy cost to start a run')
    xp = models.IntegerField(blank=True, null=True, help_text='XP gained by fully clearing the level')
    slots = models.IntegerField(
        default=4,
        help_text='Serves as general slots if dungeon does not have front/back lines'
    )

    class Meta:
        ordering = ('difficulty', 'stage')
        unique_together = ('stage', 'difficulty')

    def __str__(self):
        return f'{self.name} {self.stage} - {self.get_difficulty_display()}'


class CairossDungeon(Dungeon):
    floor = models.IntegerField()
    energy_cost = models.IntegerField(default=0, help_text='Energy cost to start a run')
    xp = models.IntegerField(blank=True, null=True, help_text='XP gained by fully clearing the level')
    slots = models.IntegerField(
        default=4,
        help_text='Serves as general slots if dungeon does not have front/back lines'
    )


class RiftRaid(Dungeon):
    DIFFICULTY_R1 = 1
    DIFFICULTY_R2 = 2
    DIFFICULTY_R3 = 3
    DIFFICULTY_R4 = 4
    DIFFICULTY_R5 = 5

    DIFFICULTY_CHOICES = (
        (DIFFICULTY_R1, 'R1'),
        (DIFFICULTY_R2, 'R2'),
        (DIFFICULTY_R3, 'R3'),
        (DIFFICULTY_R4, 'R4'),
        (DIFFICULTY_R5, 'R5'),
    )

    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES)
    energy_cost = models.IntegerField()
    frontline_slots = models.IntegerField(default=4)
    backline_slots = models.IntegerField(default=4)
    max_slots = models.IntegerField(default=6, help_text='Maximum monsters combined front/backline.')


class RiftBeast(Dungeon):
    energy_cost = models.IntegerField()
    frontline_slots = models.IntegerField(default=4)
    backline_slots = models.IntegerField(default=4)
    max_slots = models.IntegerField(default=6, help_text='Maximum monsters combined front/backline.')


class GuideBase(models.Model):
    short_text = models.TextField(blank=True, default='')
    long_text = models.TextField(blank=True, default='')
    last_updated = models.DateTimeField(auto_now=True)
    edited_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, editable=False)

    class Meta:
        abstract = True


class MonsterGuide(GuideBase):
    monster = models.OneToOneField(Monster, on_delete=models.CASCADE)

    def __str__(self):
        return f'Monster Guide - {self.monster}'

    class Meta:
        ordering = ['monster__name']
