from collections import OrderedDict

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.staticfiles.templatetags.staticfiles import static
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

    # TODO: Move this to view or something out of bestiary
    # def missing_awakening_cost(self, owner):
    #     # This calculation takes into account owned monsters which can be used as fusion ingredients.
    #     owned_ingredients = MonsterInstance.objects.filter(
    #         monster__pk__in=self.ingredients.values_list('pk', flat=True),
    #         ignore_for_fusion=False,
    #         owner=owner,
    #     )
    #     total_cost = self.total_awakening_cost(owned_ingredients)
    #     essence_storage = owner.storage.get_storage()
    #
    #     missing_essences = {
    #         element: {
    #             size: total_cost[element][size] - essence_storage[element][size] if total_cost[element][size] > essence_storage[element][size] else 0
    #             for size, qty in element_sizes.items()
    #         }
    #         for element, element_sizes in total_cost.items()
    #     }
    #
    #     # Check if there are any missing
    #     sufficient_qty = True
    #     for sizes in missing_essences.values():
    #         for qty in sizes.values():
    #             if qty > 0:
    #                 sufficient_qty = False
    #
    #     return sufficient_qty, missing_essences


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


class Dungeon(models.Model):
    CATEGORY_SCENARIO = 0
    CATEGORY_RUNE_DUNGEON = 1
    CATEGORY_ESSENCE_DUNGEON = 2
    CATEGORY_OTHER_DUNGEON = 3
    CATEGORY_RAID = 4
    CATEGORY_HALL_OF_HEROES = 5

    CATEGORY_CHOICES = [
        (CATEGORY_SCENARIO, 'Scenarios'),
        (CATEGORY_RUNE_DUNGEON, 'Rune Dungeons'),
        (CATEGORY_ESSENCE_DUNGEON, 'Elemental Dungeons'),
        (CATEGORY_OTHER_DUNGEON, 'Other Dungeons'),
        (CATEGORY_RAID, 'Raids'),
        (CATEGORY_HALL_OF_HEROES, 'Hall of Heroes'),
    ]

    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    max_floors = models.IntegerField(default=10)
    slug = models.SlugField(blank=True, null=True)
    category = models.IntegerField(choices=CATEGORY_CHOICES, blank=True, null=True)

    # TODO: Remove following fields when Level model is fully utilized everywhere: energy_cost, xp, monster_slots
    # For the following fields:
    # Outer array index is difficulty (normal, hard, hell). Inner array index is the stage/floor
    # Example: Hell B2 is dungeon.energy_cost[RunLog.DIFFICULTY_HELL][1]
    energy_cost = ArrayField(ArrayField(models.IntegerField(blank=True, null=True)), blank=True, null=True)
    xp = ArrayField(ArrayField(models.IntegerField(blank=True, null=True)), blank=True, null=True)
    monster_slots = ArrayField(ArrayField(models.IntegerField(blank=True, null=True)), blank=True, null=True)

    class Meta:
        ordering = ['id', ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Dungeon, self).save(*args, **kwargs)


class Level(models.Model):
    DIFFICULTY_NORMAL = 1
    DIFFICULTY_HARD = 2
    DIFFICULTY_HELL = 3
    DIFFICULTY_CHOICES = (
        (DIFFICULTY_NORMAL, 'Normal'),
        (DIFFICULTY_HARD, 'Hard'),
        (DIFFICULTY_HELL, 'Hell'),
    )

    dungeon = models.ForeignKey(Dungeon, on_delete=models.CASCADE)
    floor = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, blank=True, null=True)
    energy_cost = models.IntegerField(blank=True, null=True, help_text='Energy cost to start a run')
    xp = models.IntegerField(blank=True, null=True, help_text='XP gained by fully clearing the level')
    frontline_slots = models.IntegerField(
        default=5,
        help_text='Serves as general slots if dungeon does not have front/back lines'
    )
    backline_slots = models.IntegerField(blank=True, null=True, help_text='Leave null for normal dungeons')
    max_slots = models.IntegerField(
        blank=True,
        null=True,
        help_text='Maximum monsters combined front/backline. Not required if backline not specified.'
    )

    class Meta:
        ordering = ('difficulty', 'floor')
        unique_together = ('dungeon', 'floor', 'difficulty')

    def __str__(self):
        return f'{self.dungeon_id} {self.floor} - {self.get_difficulty_display()}'


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
