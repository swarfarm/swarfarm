from math import floor, ceil
import uuid
from collections import OrderedDict

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.contrib.staticfiles.templatetags.staticfiles import static

from timezone_field import TimeZoneField


# Bestiary database models
class Monster(models.Model):
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

    ELEMENT_CHOICES = (
        (ELEMENT_FIRE, 'Fire'),
        (ELEMENT_WIND, 'Wind'),
        (ELEMENT_WATER, 'Water'),
        (ELEMENT_LIGHT, 'Light'),
        (ELEMENT_DARK, 'Dark'),
    )

    TYPE_CHOICES = (
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
    com2us_id = models.IntegerField(blank=True, null=True)
    image_filename = models.CharField(max_length=250, null=True, blank=True)
    element = models.CharField(max_length=6, choices=ELEMENT_CHOICES, default=ELEMENT_FIRE)
    archetype = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_ATTACK)
    base_stars = models.IntegerField(choices=STAR_CHOICES)
    obtainable = models.BooleanField(default=True)
    can_awaken = models.BooleanField(default=True)
    is_awakened = models.BooleanField(default=False)
    awaken_bonus = models.TextField(blank=True)
    awaken_bonus_content_type = models.ForeignKey(
        ContentType,
        related_name="content_type_awaken_bonus",
        limit_choices_to=Q(app_label='herders', model='monsterskill') | Q(app_label='herders', model='monsterleaderskill'),
        null=True,
        blank=True
    )
    awaken_bonus_content_id = models.PositiveIntegerField(null=True, blank=True)
    awaken_bonus_object = GenericForeignKey('awaken_bonus_content_type', 'awaken_bonus_content_id')
    skills = models.ManyToManyField('MonsterSkill', blank=True)
    skill_ups_to_max = models.IntegerField(null=True, blank=True)
    leader_skill = models.ForeignKey('MonsterLeaderSkill', null=True, blank=True)
    base_hp = models.IntegerField(null=True, blank=True)
    base_attack = models.IntegerField(null=True, blank=True)
    base_defense = models.IntegerField(null=True, blank=True)
    max_lvl_hp = models.IntegerField(null=True, blank=True)
    max_lvl_attack = models.IntegerField(null=True, blank=True)
    max_lvl_defense = models.IntegerField(null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)
    crit_rate = models.IntegerField(null=True, blank=True)
    crit_damage = models.IntegerField(null=True, blank=True)
    resistance = models.IntegerField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)

    awakens_from = models.ForeignKey('self', null=True, blank=True, related_name='+')
    awakens_to = models.ForeignKey('self', null=True, blank=True, related_name='+')
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

    source = models.ManyToManyField('MonsterSource', blank=True)
    farmable = models.BooleanField(default=False)
    fusion_food = models.BooleanField(default=False)
    bestiary_slug = models.SlugField(max_length=255, editable=False, null=True)
    summonerswar_co_url = models.URLField(null=True, blank=True)
    wikia_url = models.URLField(null=True, blank=True)

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
                '1': {
                    'HP': self.actual_hp(grade, 1),
                    'ATK': self.actual_attack(grade, 1),
                    'DEF': self.actual_defense(grade, 1),
                },
                str(max_level): {
                    'HP': self.actual_hp(grade, max_level),
                    'ATK': self.actual_attack(grade, max_level),
                    'DEF': self.actual_defense(grade, max_level),
                },
            }

        return stats_list

    def actual_hp(self, grade, level):
        # Check that base stat exists first
        if not self.base_hp:
            return None
        else:
            return self._calculate_actual_stat(self.base_hp / 15, grade, level) * 15

    def actual_attack(self, grade=base_stars, level=1):
        # Check that base stat exists first
        if not self.base_attack:
            return None
        else:
            return self._calculate_actual_stat(self.base_attack, grade, level)

    def actual_defense(self, grade=base_stars, level=1):
        # Check that base stat exists first
        if not self.base_defense:
            return None
        else:
            return self._calculate_actual_stat(self.base_defense, grade, level)

    def _calculate_actual_stat(self, stat, grade, level):
        max_lvl = 10 + grade * 5

        weight = float(self.base_hp / 15 + self.base_attack + self.base_defense)
        base_value = round((stat * (105 + 15 * self.base_stars)) / weight, 0)

        # Magic multipliers taken from summoner's war wikia calculator. Used to calculate stats for lvl 1 and lvl MAX
        magic_multipliers = [
            {'1': 1.0, 'max': 1.9958},
            {'1': 1.5966, 'max': 3.03050646},
            {'1': 2.4242774, 'max': 4.364426603},
            {'1': 3.4914444, 'max': 5.941390935},
            {'1': 4.7529032, 'max': 8.072330795},
            {'1': 6.4582449, 'max': 10.97901633},
        ]

        stat_lvl_1 = round(base_value * magic_multipliers[grade - 1]['1'], 0)
        stat_lvl_max = round(base_value * magic_multipliers[grade - 1]['max'], 0)

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
        # Get unawakened monsters which are in the same family
        if self.is_awakened and self.awakens_from is not None:
            unawakened_name = self.awakens_from.name
        else:
            unawakened_name = self.name

        return Monster.objects.filter(name=unawakened_name).filter(obtainable=True).order_by('element')

    def all_skill_effects(self):
        return MonsterSkillEffect.objects.filter(pk__in=self.skills.exclude(skill_effect=None).values_list('skill_effect', flat=True))

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
        skip_url_gen = kwargs.pop('skip_url_gen', False)

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

        # Update the max level stats
        self.max_lvl_hp = self.actual_hp(6, 40)
        self.max_lvl_defense = self.actual_defense(6, 40)
        self.max_lvl_attack = self.actual_attack(6, 40)

        # Update image filename and slugs on save.
        if self.is_awakened and self.awakens_from:
            self.image_filename = self.awakens_from.image_filename.replace('.png', '_awakened.png')
            self.bestiary_slug = self.awakens_from.bestiary_slug
        else:
            self.image_filename = self.name.lower().replace(' ', '_') + '_' + str(self.element) + '.png'
            if self.awakens_to is not None:
                self.bestiary_slug = slugify(" ".join([self.element, self.name, self.awakens_to.name]))
            else:
                self.bestiary_slug = slugify(" ".join([self.element, self.name]))

        if not skip_url_gen:
            # Generate summonerswar.co URL if possible
            if self.can_awaken and self.base_stars > 1 and self.archetype is not self.TYPE_MATERIAL and (self.summonerswar_co_url is None or self.summonerswar_co_url == ''):
                base = 'http://summonerswar.co/'
                try:
                    # Generate the URL
                    if self.is_awakened:
                        unawakened_name = self.awakens_from.name
                        awakened_name = self.name
                    else:
                        unawakened_name = self.name
                        awakened_name = self.awakens_to.name

                    url = base + slugify(self.element + '-' + unawakened_name + '-' + awakened_name)

                    # Check that it is valid
                    from urllib2 import Request, urlopen
                    request = Request(url)
                    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36')
                    code = urlopen(request).code
                    if code == 200:
                        self.summonerswar_co_url = url
                    else:
                        self.summonerswar_co_url = None
                except:
                    # Something prevented getting the correct names or verifying the URL, so clear it out
                    self.summonerswar_co_url = None

            # Generate wikia URL if possible
            if self.wikia_url is None or self.wikia_url == '':
                base = 'http://summonerswar.wikia.com/wiki/'
                try:
                    # Generate the URL
                    if self.is_awakened:
                        unawakened_name = self.awakens_from.name
                    else:
                        unawakened_name = self.name

                    url = base + unawakened_name.replace(' ', '_') + '_(' + self.get_element_display() + ')'

                    # Check that it is valid
                    from urllib2 import Request, urlopen
                    request = Request(url)
                    request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36')
                    code = urlopen(request).code
                    if code == 200:
                        self.wikia_url = url
                    else:
                        self.wikia_url = None
                except:
                    # Something prevented getting the correct names or verifying the URL, so clear it out
                    self.wikia_url = None

        # Pull info from unawakened version of this monster. This copying of data is one directional only
        if self.awakens_from:
            # Copy awaken bonus from unawakened version
            if self.is_awakened and self.awakens_from.awaken_bonus:
                self.awaken_bonus = self.awakens_from.awaken_bonus
                self.awaken_bonus_content_type = self.awakens_from.awaken_bonus_content_type
                self.awaken_bonus_content_id = self.awakens_from.awaken_bonus_content_id

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

    def __unicode__(self):
        if self.is_awakened:
            return self.name
        else:
            return self.name + ' (' + self.element.capitalize() + ')'


class MonsterSkill(models.Model):
    name = models.CharField(max_length=40)
    com2us_id = models.IntegerField(blank=True, null=True)
    description = models.TextField()
    slot = models.IntegerField(default=1)
    skill_effect = models.ManyToManyField('MonsterSkillEffect', blank=True)
    effect = models.ManyToManyField('MonsterSkillEffect', through='MonsterSkillEffectDetail', blank=True, related_name='effect')
    cooltime = models.IntegerField(null=True, blank=True)
    passive = models.BooleanField(default=False)
    max_level = models.IntegerField()
    level_progress_description = models.TextField(null=True, blank=True)
    icon_filename = models.CharField(max_length=100, null=True, blank=True)
    atk_multiplier = models.IntegerField(blank=True, null=True)
    scales_with = models.ManyToManyField('MonsterSkillScalingStat', through='MonsterSkillScalesWith')

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/skills/' + self.icon_filename))
        else:
            return 'No Image'

    def level_progress_description_list(self):
        return self.level_progress_description.splitlines()

    def __unicode__(self):
        return self.name + ' - ' + self.icon_filename

    class Meta:
        ordering = ['slot', 'name']


class MonsterLeaderSkill(models.Model):
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

    attribute = models.IntegerField(choices=ATTRIBUTE_CHOICES)
    amount = models.IntegerField()
    area = models.IntegerField(choices=AREA_CHOICES, default=AREA_GENERAL)
    element = models.CharField(max_length=6, null=True, blank=True, choices=Monster.ELEMENT_CHOICES)

    def skill_string(self):
        if self.area == self.AREA_DUNGEON:
            condition = 'in the Dungeons '
        elif self.area == self.AREA_ARENA:
            condition = 'in the Arena '
        elif self.area == self.AREA_GUILD:
            condition = 'in the Guild Battles '
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

    def __unicode__(self):
        if self.area == self.AREA_ELEMENT:
            condition = ' {}'.format(self.get_element_display())
        elif self.area == self.AREA_GENERAL:
            condition = ''
        else:
            condition = ' {}'.format(self.get_area_display())

        return self.get_attribute_display() + ' ' + str(self.amount) + '%' + condition

    class Meta:
        ordering = ['attribute', 'amount', 'element']


class MonsterSkillEffectBuffsManager(models.Manager):
    def get_queryset(self):
        return super(MonsterSkillEffectBuffsManager, self).get_queryset().values_list('pk', 'icon_filename').filter(is_buff=True).exclude(icon_filename='')


class MonsterSkillEffectDebuffsManager(models.Manager):
    def get_queryset(self):
        return super(MonsterSkillEffectDebuffsManager, self).get_queryset().values_list('pk', 'icon_filename').filter(is_buff=False).exclude(icon_filename='')


class MonsterSkillEffectOtherManager(models.Manager):
    def get_queryset(self):
        return super(MonsterSkillEffectOtherManager, self).get_queryset().values_list('pk', 'name').filter(icon_filename='')


class MonsterSkillEffect(models.Model):
    is_buff = models.BooleanField(default=True)
    name = models.CharField(max_length=40)
    description = models.TextField()
    icon_filename = models.CharField(max_length=100, null=True, blank=True)

    objects = models.Manager()
    buff_effect_choices = MonsterSkillEffectBuffsManager()
    debuff_effect_choices = MonsterSkillEffectDebuffsManager()
    other_effect_choices = MonsterSkillEffectOtherManager()

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/buffs/' + self.icon_filename))
        else:
            return 'No Image'

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-is_buff', 'name']


class MonsterSkillEffectDetail(models.Model):
    skill = models.ForeignKey(MonsterSkill, on_delete=models.CASCADE)
    effect = models.ForeignKey(MonsterSkillEffect, on_delete=models.CASCADE)
    aoe = models.BooleanField(default=False, help_text='Effect applies to entire friendly or enemy group')
    single_target = models.BooleanField(default=False, help_text='Effect applies to a single monster')
    self_effect = models.BooleanField(default=False, help_text='Effect applies to the monster using the skill')
    random = models.BooleanField(default=False, help_text='Skill effect applies randomly to the target')
    quantity = models.IntegerField(default=0, help_text='Number of items this effect affects on the target')
    all = models.BooleanField(default=False, help_text='This effect affects all items on the target')


class MonsterSkillScalingStat(models.Model):
    stat = models.CharField(max_length=20)

    def __unicode__(self):
        return self.stat


class MonsterSkillScalesWith(models.Model):
    scalingstat = models.ForeignKey(MonsterSkillScalingStat)
    monsterskill = models.ForeignKey(MonsterSkill)
    multiplier = models.IntegerField(blank=True, null=True)


class MonsterSource(models.Model):
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

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['meta_order', 'icon_filename', 'name']


class Fusion(models.Model):
    product = models.ForeignKey('Monster', related_name='product')
    stars = models.IntegerField()
    cost = models.IntegerField()
    ingredients = models.ManyToManyField('Monster')
    meta_order = models.IntegerField(db_index=True, default=0)

    def __unicode__(self):
        return str(self.product) + ' Fusion'

    class Meta:
        ordering = ['meta_order']


# Individual user/monster collection models
class Summoner(models.Model):
    user = models.OneToOneField(User)
    summoner_name = models.CharField(max_length=256, null=True, blank=True)
    com2us_id = models.BigIntegerField(default=None, null=True, blank=True)
    global_server = models.NullBooleanField(default=True, null=True, blank=True)
    following = models.ManyToManyField("self", related_name='followed_by', symmetrical=False)
    public = models.BooleanField(default=False, blank=True)
    timezone = TimeZoneField(default='America/Los_Angeles')
    notes = models.TextField(null=True, blank=True)
    storage_magic_low = models.IntegerField(default=0)
    storage_magic_mid = models.IntegerField(default=0)
    storage_magic_high = models.IntegerField(default=0)
    storage_fire_low = models.IntegerField(default=0)
    storage_fire_mid = models.IntegerField(default=0)
    storage_fire_high = models.IntegerField(default=0)
    storage_water_low = models.IntegerField(default=0)
    storage_water_mid = models.IntegerField(default=0)
    storage_water_high = models.IntegerField(default=0)
    storage_wind_low = models.IntegerField(default=0)
    storage_wind_mid = models.IntegerField(default=0)
    storage_wind_high = models.IntegerField(default=0)
    storage_light_low = models.IntegerField(default=0)
    storage_light_mid = models.IntegerField(default=0)
    storage_light_high = models.IntegerField(default=0)
    storage_dark_low = models.IntegerField(default=0)
    storage_dark_mid = models.IntegerField(default=0)
    storage_dark_high = models.IntegerField(default=0)

    def get_storage(self):
        storage = OrderedDict()
        storage['magic'] = OrderedDict()
        storage['magic']['low'] = self.storage_magic_low
        storage['magic']['mid'] = self.storage_magic_mid
        storage['magic']['high'] = self.storage_magic_high
        storage['fire'] = OrderedDict()
        storage['fire']['low'] = self.storage_fire_low
        storage['fire']['mid'] = self.storage_fire_mid
        storage['fire']['high'] = self.storage_fire_high
        storage['water'] = OrderedDict()
        storage['water']['low'] = self.storage_water_low
        storage['water']['mid'] = self.storage_water_mid
        storage['water']['high'] = self.storage_water_high
        storage['wind'] = OrderedDict()
        storage['wind']['low'] = self.storage_wind_low
        storage['wind']['mid'] = self.storage_wind_mid
        storage['wind']['high'] = self.storage_wind_high
        storage['light'] = OrderedDict()
        storage['light']['low'] = self.storage_light_low
        storage['light']['mid'] = self.storage_light_mid
        storage['light']['high'] = self.storage_light_high
        storage['dark'] = OrderedDict()
        storage['dark']['low'] = self.storage_dark_low
        storage['dark']['mid'] = self.storage_dark_mid
        storage['dark']['high'] = self.storage_dark_high

        return storage

    def get_rune_counts(self):
        counts = {}

        for rune_type in RuneInstance.TYPE_CHOICES:
            counts[rune_type[1]] = RuneInstance.objects.filter(owner=self, type=rune_type[0]).count()

        return counts

    def save(self, *args, **kwargs):
        # Bounds checks on essences
        if self.storage_magic_low < 0:
            self.storage_magic_low = 0
        if self.storage_magic_mid < 0:
            self.storage_magic_mid = 0
        if self.storage_magic_high < 0:
            self.storage_magic_high = 0

        if self.storage_fire_low < 0:
            self.storage_fire_low = 0
        if self.storage_fire_mid < 0:
            self.storage_fire_mid = 0
        if self.storage_fire_high < 0:
            self.storage_fire_high = 0

        if self.storage_wind_low < 0:
            self.storage_wind_low = 0
        if self.storage_wind_mid < 0:
            self.storage_wind_mid = 0
        if self.storage_wind_high < 0:
            self.storage_wind_high = 0

        if self.storage_water_low < 0:
            self.storage_water_low = 0
        if self.storage_water_mid < 0:
            self.storage_water_mid = 0
        if self.storage_water_high < 0:
            self.storage_water_high = 0

        if self.storage_dark_low < 0:
            self.storage_dark_low = 0
        if self.storage_dark_mid < 0:
            self.storage_dark_mid = 0
        if self.storage_dark_high < 0:
            self.storage_dark_high = 0

        if self.storage_light_low < 0:
            self.storage_light_low = 0
        if self.storage_light_mid < 0:
            self.storage_light_mid = 0
        if self.storage_light_high < 0:
            self.storage_light_high = 0

        super(Summoner, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s" % self.user


class MonsterInstanceImportedManager(models.Manager):
    def get_queryset(self):
        return super(MonsterInstanceImportedManager, self).get_queryset().filter(uncommitted=True)


class MonsterInstanceManager(models.Manager):
    # Default manager which only returns finalized instances
    def get_queryset(self):
        return super(MonsterInstanceManager, self).get_queryset().filter(uncommitted=False)


class MonsterInstance(models.Model):
    PRIORITY_DONE = 0
    PRIORITY_LOW = 1
    PRIORITY_MED = 2
    PRIORITY_HIGH = 3

    PRIORITY_CHOICES = (
        (PRIORITY_DONE, 'Done'),
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MED, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    )

    # Multiple managers to split out imported and finalized objects
    objects = models.Manager()
    committed = MonsterInstanceManager()
    imported = MonsterInstanceImportedManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('Summoner')
    monster = models.ForeignKey('Monster')
    com2us_id = models.BigIntegerField(blank=True, null=True)
    created = models.DateTimeField(blank=True, null=True)
    stars = models.IntegerField()
    level = models.IntegerField()
    skill_1_level = models.IntegerField(blank=True, default=1)
    skill_2_level = models.IntegerField(blank=True, default=1)
    skill_3_level = models.IntegerField(blank=True, default=1)
    skill_4_level = models.IntegerField(blank=True, default=1)
    base_hp = models.IntegerField(blank=True, default=0)
    rune_hp = models.IntegerField(blank=True, default=0)
    base_attack = models.IntegerField(blank=True, default=0)
    rune_attack = models.IntegerField(blank=True, default=0)
    base_defense = models.IntegerField(blank=True, default=0)
    rune_defense = models.IntegerField(blank=True, default=0)
    base_speed = models.IntegerField(blank=True, default=0)
    rune_speed = models.IntegerField(blank=True, default=0)
    base_crit_rate = models.IntegerField(blank=True, default=0)
    rune_crit_rate = models.IntegerField(blank=True, default=0)
    base_crit_damage = models.IntegerField(blank=True, default=0)
    rune_crit_damage = models.IntegerField(blank=True, default=0)
    base_resistance = models.IntegerField(blank=True, default=0)
    rune_resistance = models.IntegerField(blank=True, default=0)
    base_accuracy = models.IntegerField(blank=True, default=0)
    rune_accuracy = models.IntegerField(blank=True, default=0)

    fodder = models.BooleanField(default=False)
    in_storage = models.BooleanField(default=False)
    ignore_for_fusion = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_MED)
    notes = models.TextField(null=True, blank=True, help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    uncommitted = models.BooleanField(default=False)  # Used for importing

    def is_max_level(self):
        return self.level == self.monster.max_level_from_stars(self.stars)

    def max_level_from_stars(self):
        return self.monster.max_level_from_stars(self.stars)

    def skill_ups_to_max(self):
        skill_ups_remaining = self.monster.skill_ups_to_max
        skill_levels = [self.skill_1_level, self.skill_2_level, self.skill_3_level, self.skill_4_level]

        for idx in range(0, self.monster.skills.count()):
            skill_ups_remaining -= skill_levels[idx] - 1

        return skill_ups_remaining

    def get_rune_set_bonuses(self):
        from django.db.models import Count
        rune_counts = self.runeinstance_set.values('type').order_by().annotate(count=Count('type'))
        rune_bonuses = []

        for rune_count in rune_counts:
            type_name = RuneInstance.TYPE_CHOICES[rune_count['type'] - 1][1]
            required = RuneInstance.RUNE_SET_COUNT_REQUIREMENTS[rune_count['type']]
            present = rune_count['count']
            bonus_text = RuneInstance.RUNE_SET_BONUSES[rune_count['type']]

            if present >= required:
                rune_bonuses.extend([type_name + ' ' + bonus_text] * (present // required))

        return rune_bonuses

    # Rune bonus calculations
    def rune_bonus_energy(self):
        set_bonus_count = floor(self.runeinstance_set.filter(type=RuneInstance.TYPE_ENERGY).count() / 2)
        return ceil(self.base_hp * 0.15) * set_bonus_count

    def rune_bonus_fatal(self):
        if self.runeinstance_set.filter(type=RuneInstance.TYPE_FATAL).count() >= 4:
            return ceil(self.base_attack * 0.35)
        else:
            return 0

    def rune_bonus_blade(self):
        rune_count = self.runeinstance_set.filter(type=RuneInstance.TYPE_BLADE).count()
        return 12 * floor(rune_count / 2)

    def rune_bonus_rage(self):
        if self.runeinstance_set.filter(type=RuneInstance.TYPE_RAGE).count() >= 4:
            return 40
        else:
            return 0

    def rune_bonus_swift(self):
        if self.runeinstance_set.filter(type=RuneInstance.TYPE_SWIFT).count() >= 4:
            return 25
        else:
            return 0

    def rune_bonus_focus(self):
        rune_count = self.runeinstance_set.filter(type=RuneInstance.TYPE_FOCUS).count()
        return 20 * floor(rune_count / 2)

    def rune_bonus_guard(self):
        set_bonus_count = floor(self.runeinstance_set.filter(type=RuneInstance.TYPE_GUARD).count() / 2)
        return ceil(self.base_defense * 0.15) * set_bonus_count

    def rune_bonus_endure(self):
        rune_count = self.runeinstance_set.filter(type=RuneInstance.TYPE_ENDURE).count()
        return 20 * floor(rune_count / 2)

    # Stat callables. Base = monster's own stat. Rune = amount gained from runes. Stat by itself is combined total
    def calc_base_hp(self):
        return self.monster.actual_hp(self.stars, self.level)

    def calc_rune_hp(self):
        runes = self.runeinstance_set.filter(has_hp=True)
        base = self.base_hp
        hp_percent = 0
        hp_flat = 0

        for rune in runes:
            hp_flat += rune.get_stat(RuneInstance.STAT_HP)
            hp_percent += rune.get_stat(RuneInstance.STAT_HP_PCT)

        rune_set_bonus = self.rune_bonus_energy()

        return int(ceil(base * (hp_percent / 100.0)) + rune_set_bonus + hp_flat)

    def hp(self):
        return self.base_hp + self.rune_hp

    def calc_base_attack(self):
        return self.monster.actual_attack(self.stars, self.level)

    def calc_rune_attack(self):
        runes = self.runeinstance_set.filter(has_atk=True)
        base = self.base_attack
        atk_percent = 0
        atk_flat = 0

        for rune in runes:
            atk_flat += rune.get_stat(RuneInstance.STAT_ATK)
            atk_percent += rune.get_stat(RuneInstance.STAT_ATK_PCT)

        rune_set_bonus = self.rune_bonus_fatal()

        return int(ceil(base * (atk_percent / 100.0)) + rune_set_bonus + atk_flat)

    def attack(self):
        return self.base_attack + self.rune_attack

    def calc_base_defense(self):
        return self.monster.actual_defense(self.stars, self.level)

    def calc_rune_defense(self):
        runes = self.runeinstance_set.filter(has_def=True)
        base = self.base_defense
        def_percent = 0
        def_flat = 0

        for rune in runes:
            def_flat += rune.get_stat(RuneInstance.STAT_DEF)
            def_percent += rune.get_stat(RuneInstance.STAT_DEF_PCT)

        rune_set_bonus = self.rune_bonus_guard()

        return int(ceil(base * (def_percent / 100.0)) + rune_set_bonus + def_flat)

    def defense(self):
        return self.base_defense + self.rune_defense

    def calc_base_speed(self):
        return self.monster.speed

    def calc_rune_speed(self):
        base = self.base_speed
        runes = self.runeinstance_set.filter(has_speed=True)
        spd_percent = self.rune_bonus_swift()
        spd_flat = 0

        for rune in runes:
            spd_flat += rune.get_stat(RuneInstance.STAT_SPD)

        return int(ceil(base * (spd_percent / 100.0)) + spd_flat)

    def speed(self):
        return self.base_speed + self.rune_speed

    def calc_base_crit_rate(self):
        return self.monster.crit_rate

    def calc_rune_crit_rate(self):
        runes = self.runeinstance_set.filter(has_crit_rate=True)
        crit_rate = self.rune_bonus_blade()

        for rune in runes:
            crit_rate += rune.get_stat(RuneInstance.STAT_CRIT_RATE_PCT)

        return int(crit_rate)

    def crit_rate(self):
        return self.base_crit_rate + self.rune_crit_rate

    def calc_base_crit_damage(self):
        return self.monster.crit_damage

    def calc_rune_crit_damage(self):
        runes = self.runeinstance_set.filter(has_crit_dmg=True)
        crit_damage = self.rune_bonus_rage()

        for rune in runes:
            crit_damage += rune.get_stat(RuneInstance.STAT_CRIT_DMG_PCT)

        return int(crit_damage)

    def crit_damage(self):
        return self.base_crit_damage + self.rune_crit_damage

    def calc_base_resistance(self):
        return self.monster.resistance

    def calc_rune_resistance(self):
        runes = self.runeinstance_set.filter(has_resist=True)
        resist = self.rune_bonus_endure()

        for rune in runes:
            resist += rune.get_stat(RuneInstance.STAT_RESIST_PCT)

        return int(resist)

    def resistance(self):
        return self.base_resistance + self.rune_resistance

    def calc_base_accuracy(self):
        return self.monster.accuracy

    def calc_rune_accuracy(self):
        runes = self.runeinstance_set.filter(has_accuracy=True)
        accuracy = self.rune_bonus_focus()

        for rune in runes:
            accuracy += rune.get_stat(RuneInstance.STAT_ACCURACY_PCT)

        return int(accuracy)

    def accuracy(self):
        return self.base_accuracy + self.rune_accuracy

    def update_fields(self):
        # Update stats
        self.base_hp = self.calc_base_hp()
        self.base_attack = self.calc_base_attack()
        self.base_defense = self.calc_base_defense()
        self.base_speed = self.calc_base_speed()
        self.base_crit_rate = self.calc_base_crit_rate()
        self.base_crit_damage = self.calc_base_crit_damage()
        self.base_resistance = self.calc_base_resistance()
        self.base_accuracy = self.calc_base_accuracy()

        self.rune_hp = self.calc_rune_hp()
        self.rune_attack = self.calc_rune_attack()
        self.rune_defense = self.calc_rune_defense()
        self.rune_speed = self.calc_rune_speed()
        self.rune_crit_rate = self.calc_rune_crit_rate()
        self.rune_crit_damage = self.calc_rune_crit_damage()
        self.rune_resistance = self.calc_rune_resistance()
        self.rune_accuracy = self.calc_rune_accuracy()

        # Limit skill levels to the max level of the skill
        skills = self.monster.skills.all()

        if len(skills) >= 1 and self.skill_1_level > skills[0].max_level:
            self.skill_1_level = skills[0].max_level

        if len(skills) >= 2 and self.skill_2_level > skills[1].max_level:
            self.skill_2_level = skills[1].max_level

        if len(skills) >= 3 and self.skill_3_level > skills[2].max_level:
            self.skill_3_level = skills[2].max_level

        if len(skills) >= 4 and self.skill_4_level > skills[3].max_level:
            self.skill_4_level = skills[3].max_level

    def clean(self):
        from django.core.exceptions import ValidationError, ObjectDoesNotExist

        # Check skill levels
        if self.skill_1_level is None or self.skill_1_level < 1:
            self.skill_1_level = 1
        if self.skill_2_level is None or self.skill_2_level < 1:
            self.skill_2_level = 1
        if self.skill_3_level is None or self.skill_3_level < 1:
            self.skill_3_level = 1
        if self.skill_4_level is None or self.skill_4_level < 1:
            self.skill_4_level = 1

        if self.level > 40 or self.level < 1:
            raise ValidationError(
                'Level out of range (Valid range %(min)s-%(max)s)',
                params={'min': 1, 'max': 40},
                code='invalid_level'
            )

        if self.stars and (self.level > 10 + self.stars * 5):
            raise ValidationError(
                'Level exceeds max for given star rating (Max: %(value)s)',
                params={'value': 10 + self.stars * 5},
                code='invalid_level'
            )

        try:
            min_stars = self.monster.base_stars
            if self.monster.is_awakened:
                min_stars -= 1
        except ObjectDoesNotExist:
            min_stars = 1

        if self.stars and (self.stars > 6 or self.stars < min_stars):
            raise ValidationError(
                'Star rating out of range (%(min)s to %(max)s)',
                params={'min': min_stars, 'max': 6},
                code='invalid_stars'
            )

        super(MonsterInstance, self).clean()

    def save(self, *args, **kwargs):
        self.update_fields()
        super(MonsterInstance, self).save(*args, **kwargs)

    def __unicode__(self):
        return str(self.monster) + ', ' + str(self.stars) + '*, Lvl ' + str(self.level)

    class Meta:
        ordering = ['-stars', '-level', 'monster__name']


class MonsterPieceImportedManager(models.Manager):
    def get_queryset(self):
        return super(MonsterPieceImportedManager, self).get_queryset().filter(uncommitted=True)


class MonsterPieceManager(models.Manager):
    # Default manager which only returns finalized instances
    def get_queryset(self):
        return super(MonsterPieceManager, self).get_queryset().filter(uncommitted=False)


class MonsterPiece(models.Model):
    # Multiple managers to split out imported and finalized objects
    objects = models.Manager()
    committed = MonsterPieceManager()
    imported = MonsterPieceImportedManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('Summoner')
    monster = models.ForeignKey('Monster')
    pieces = models.IntegerField(default=0)
    uncommitted = models.BooleanField(default=False)  # Used for importing

    class Meta:
        ordering = ['monster__name']

    def __str__(self):
        return str(self.monster) + ' - ' + str(self.pieces) + ' pieces'

    def can_summon(self):
        piece_requirements = {
            1: 10,
            2: 20,
            3: 40,
            4: 50,
            5: 100,
        }
        base_stars = self.monster.base_stars

        if self.monster.is_awakened:
            base_stars -= 1

        return self.pieces > piece_requirements[base_stars]


class RuneInstanceImportedManager(models.Manager):
    def get_queryset(self):
        return super(RuneInstanceImportedManager, self).get_queryset().filter(uncommitted=True)


class RuneInstanceManager(models.Manager):
    # Default manager which only returns finalized instances
    def get_queryset(self):
        return super(RuneInstanceManager, self).get_queryset().filter(uncommitted=False)


class RuneInstance(models.Model):
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

    # This list of tuples is used for display of rune stats
    RUNE_STAT_DISPLAY = {
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

    MAIN_STAT_RANGES = {
        STAT_HP: {
            1: {'min': 40, 'max': 804},
            2: {'min': 70, 'max': 1092},
            3: {'min': 100, 'max': 1380},
            4: {'min': 160, 'max': 1704},
            5: {'min': 270, 'max': 2088},
            6: {'min': 360, 'max': 2448},
        },
        STAT_HP_PCT: {
            1: {'min': 1, 'max': 18},
            2: {'min': 2, 'max': 20},
            3: {'min': 4, 'max': 38},
            4: {'min': 5, 'max': 43},
            5: {'min': 8, 'max': 51},
            6: {'min': 11, 'max': 63},
        },
        STAT_ATK: {
            1: {'min': 3, 'max': 54},
            2: {'min': 5, 'max': 74},
            3: {'min': 7, 'max': 93},
            4: {'min': 10, 'max': 113},
            5: {'min': 15, 'max': 135},
            6: {'min': 22, 'max': 160},
        },
        STAT_SPD: {
            1: {'min': 1, 'max': 18},
            2: {'min': 2, 'max': 19},
            3: {'min': 3, 'max': 25},
            4: {'min': 4, 'max': 30},
            5: {'min': 5, 'max': 39},
            6: {'min': 7, 'max': 42},
        },
        STAT_CRIT_RATE_PCT: {
            1: {'min': 1, 'max': 18},
            2: {'min': 2, 'max': 20},
            3: {'min': 4, 'max': 37},
            4: {'min': 5, 'max': 41},
            5: {'min': 8, 'max': 47},
            6: {'min': 11, 'max': 58},
        },
        STAT_CRIT_DMG_PCT: {
            1: {'min': 2, 'max': 20},
            2: {'min': 3, 'max': 37},
            3: {'min': 4, 'max': 43},
            4: {'min': 6, 'max': 58},
            5: {'min': 9, 'max': 65},
            6: {'min': 12, 'max': 80},
        },
        STAT_RESIST_PCT: {
            1: {'min': 1, 'max': 18},
            2: {'min': 2, 'max': 20},
            3: {'min': 4, 'max': 38},
            4: {'min': 6, 'max': 44},
            5: {'min': 9, 'max': 51},
            6: {'min': 12, 'max': 64},
        },
    }

    SUBSTAT_MAX_VALUES = {
        STAT_HP_PCT: 40.0,
        STAT_ATK_PCT: 40.0,
        STAT_DEF_PCT: 40.0,
        STAT_SPD: 30.0,
        STAT_CRIT_RATE_PCT: 30.0,
        STAT_CRIT_DMG_PCT: 35.0,
        STAT_RESIST_PCT: 40.0,
        STAT_ACCURACY_PCT: 40.0,
    }

    INNATE_STAT_TITLES = {
        STAT_HP: 'Strong',
        STAT_HP_PCT: 'Tenacious',
        STAT_ATK: 'Ferocious',
        STAT_ATK_PCT: 'Powerful',
        STAT_DEF: 'Sturdy',
        STAT_DEF_PCT: 'Durable',
        STAT_SPD: 'Quick',
        STAT_CRIT_RATE_PCT: 'Mortal',
        STAT_CRIT_DMG_PCT: 'Cruel',
        STAT_RESIST_PCT: 'Resistant',
        STAT_ACCURACY_PCT: 'Intricate',
    }

    # Copy a few ranges that are the same
    MAIN_STAT_RANGES[STAT_ATK_PCT] = MAIN_STAT_RANGES[STAT_HP_PCT]
    MAIN_STAT_RANGES[STAT_DEF] = MAIN_STAT_RANGES[STAT_ATK]
    MAIN_STAT_RANGES[STAT_DEF_PCT] = MAIN_STAT_RANGES[STAT_HP_PCT]
    MAIN_STAT_RANGES[STAT_ACCURACY_PCT] = MAIN_STAT_RANGES[STAT_RESIST_PCT]

    RUNE_SET_COUNT_REQUIREMENTS = {
        TYPE_ENERGY: 2,
        TYPE_FATAL: 4,
        TYPE_BLADE: 2,
        TYPE_RAGE: 4,
        TYPE_SWIFT: 4,
        TYPE_FOCUS: 2,
        TYPE_GUARD: 2,
        TYPE_ENDURE: 2,
        TYPE_VIOLENT: 4,
        TYPE_WILL: 2,
        TYPE_NEMESIS: 2,
        TYPE_SHIELD: 2,
        TYPE_REVENGE: 2,
        TYPE_DESPAIR: 4,
        TYPE_VAMPIRE: 4,
        TYPE_DESTROY: 2,
    }

    RUNE_SET_BONUSES = {
        TYPE_ENERGY: '2 Set: HP +15%',
        TYPE_FATAL: '4 Set: Attack Power +35%',
        TYPE_BLADE: '2 Set: Critical Rate +12%',
        TYPE_RAGE: '4 Set: Critical Damage +40%',
        TYPE_SWIFT: '4 Set: Attack Speed +25%',
        TYPE_FOCUS: '2 Set: Accuracy +20%',
        TYPE_GUARD: '2 Set: Defense +15%',
        TYPE_ENDURE: '2 Set: Resistance +20%',
        TYPE_VIOLENT: '4 Set: Get Extra Turn +22%',
        TYPE_WILL: '2 Set: Immunity +1 turn',
        TYPE_NEMESIS: '2 Set: ATK Gauge +4% (for every 7% HP lost)',
        TYPE_SHIELD: '2 Set: Ally Shield 3 turns (15% of HP)',
        TYPE_REVENGE: '2 Set: Counterattack +15%',
        TYPE_DESPAIR: '4 Set: Stun Rate +25%',
        TYPE_VAMPIRE: '4 Set: Life Drain +35%',
        TYPE_DESTROY: "2 Set: 30% of the damage dealt will reduce up to 4% of the enemy's Max HP"
    }

    # Multiple managers to split out imported and finalized objects
    objects = models.Manager()
    committed = RuneInstanceManager()
    imported = RuneInstanceImportedManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.IntegerField(choices=TYPE_CHOICES)
    owner = models.ForeignKey(Summoner)
    com2us_id = models.BigIntegerField(blank=True, null=True)
    assigned_to = models.ForeignKey(MonsterInstance, blank=True, null=True, )
    stars = models.IntegerField()
    level = models.IntegerField()
    slot = models.IntegerField()
    value = models.IntegerField(blank=True, null=True)
    main_stat = models.IntegerField(choices=STAT_CHOICES)
    main_stat_value = models.IntegerField(default=0)
    innate_stat = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    innate_stat_value = models.IntegerField(null=True, blank=True)
    substat_1 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_1_value = models.IntegerField(null=True, blank=True)
    substat_2 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_2_value = models.IntegerField(null=True, blank=True)
    substat_3 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_3_value = models.IntegerField(null=True, blank=True)
    substat_4 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_4_value = models.IntegerField(null=True, blank=True)
    marked_for_sale = models.BooleanField(default=False)
    uncommitted = models.BooleanField(default=False)  # Used for importing

    # The following fields exist purely to allow easier filtering and are updated on model save
    quality = models.IntegerField(default=0, choices=QUALITY_CHOICES)
    has_hp = models.BooleanField(default=False)
    has_atk = models.BooleanField(default=False)
    has_def = models.BooleanField(default=False)
    has_crit_rate = models.BooleanField(default=False)
    has_crit_dmg = models.BooleanField(default=False)
    has_speed = models.BooleanField(default=False)
    has_resist = models.BooleanField(default=False)
    has_accuracy = models.BooleanField(default=False)
    efficiency = models.FloatField(blank=True, null=True)

    def get_main_stat_rune_display(self):
        return self.RUNE_STAT_DISPLAY.get(self.main_stat, '')

    def get_innate_stat_rune_display(self):
        return self.RUNE_STAT_DISPLAY.get(self.innate_stat, '')

    def get_substat_1_rune_display(self):
        return self.RUNE_STAT_DISPLAY.get(self.substat_1, '')

    def get_substat_2_rune_display(self):
        return self.RUNE_STAT_DISPLAY.get(self.substat_2, '')

    def get_substat_3_rune_display(self):
        return self.RUNE_STAT_DISPLAY.get(self.substat_3, '')

    def get_substat_4_rune_display(self):
        return self.RUNE_STAT_DISPLAY.get(self.substat_4, '')

    def get_rune_set_bonus(self):
        return self.RUNE_SET_BONUSES[self.type]

    @staticmethod
    def get_valid_stats_for_slot(slot):
        if slot == 1:
            return {
                RuneInstance.STAT_ATK: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ATK - 1][1],
            }
        elif slot == 2:
            return {
                RuneInstance.STAT_ATK: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ATK - 1][1],
                RuneInstance.STAT_ATK_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ATK_PCT - 1][1],
                RuneInstance.STAT_DEF: RuneInstance.STAT_CHOICES[RuneInstance.STAT_DEF - 1][1],
                RuneInstance.STAT_DEF_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_DEF_PCT - 1][1],
                RuneInstance.STAT_HP: RuneInstance.STAT_CHOICES[RuneInstance.STAT_HP - 1][1],
                RuneInstance.STAT_HP_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_HP_PCT - 1][1],
                RuneInstance.STAT_SPD: RuneInstance.STAT_CHOICES[RuneInstance.STAT_SPD - 1][1],
            }
        elif slot == 3:
            return {
                RuneInstance.STAT_DEF: RuneInstance.STAT_CHOICES[RuneInstance.STAT_DEF - 1][1],
            }
        elif slot == 4:
            return {
                RuneInstance.STAT_ATK: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ATK - 1][1],
                RuneInstance.STAT_ATK_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ATK_PCT - 1][1],
                RuneInstance.STAT_DEF: RuneInstance.STAT_CHOICES[RuneInstance.STAT_DEF - 1][1],
                RuneInstance.STAT_DEF_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_DEF_PCT - 1][1],
                RuneInstance.STAT_HP: RuneInstance.STAT_CHOICES[RuneInstance.STAT_HP - 1][1],
                RuneInstance.STAT_HP_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_HP_PCT - 1][1],
                RuneInstance.STAT_CRIT_RATE_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_CRIT_RATE_PCT - 1][1],
                RuneInstance.STAT_CRIT_DMG_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_CRIT_DMG_PCT - 1][1],
            }
        elif slot == 5:
            return {
                RuneInstance.STAT_HP: RuneInstance.STAT_CHOICES[RuneInstance.STAT_HP - 1][1],
            }
        elif slot == 6:
            return {
                RuneInstance.STAT_ATK: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ATK - 1][1],
                RuneInstance.STAT_ATK_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ATK_PCT - 1][1],
                RuneInstance.STAT_DEF: RuneInstance.STAT_CHOICES[RuneInstance.STAT_DEF - 1][1],
                RuneInstance.STAT_DEF_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_DEF_PCT - 1][1],
                RuneInstance.STAT_HP: RuneInstance.STAT_CHOICES[RuneInstance.STAT_HP - 1][1],
                RuneInstance.STAT_HP_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_HP_PCT - 1][1],
                RuneInstance.STAT_RESIST_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_RESIST_PCT - 1][1],
                RuneInstance.STAT_ACCURACY_PCT: RuneInstance.STAT_CHOICES[RuneInstance.STAT_ACCURACY_PCT - 1][1],
            }
        else:
            return None

    def get_stat(self, stat_type, sub_stats_only=False):
        if self.main_stat == stat_type and not sub_stats_only:
            return self.main_stat_value
        elif self.innate_stat == stat_type and not sub_stats_only:
            return self.innate_stat_value
        elif self.substat_1 == stat_type:
            return self.substat_1_value
        elif self.substat_2 == stat_type:
            return self.substat_2_value
        elif self.substat_3 == stat_type:
            return self.substat_3_value
        elif self.substat_4 == stat_type:
            return self.substat_4_value
        else:
            return 0

    # Individual functions for each stat to use within templates
    def get_hp_pct(self):
        return self.get_stat(RuneInstance.STAT_HP_PCT, False)

    def get_hp(self):
        return self.get_stat(RuneInstance.STAT_HP, False)

    def get_def_pct(self):
        return self.get_stat(RuneInstance.STAT_DEF_PCT, False)

    def get_def(self):
        return self.get_stat(RuneInstance.STAT_DEF, False)

    def get_atk_pct(self):
        return self.get_stat(RuneInstance.STAT_ATK_PCT, False)

    def get_atk(self):
        return self.get_stat(RuneInstance.STAT_ATK, False)

    def get_spd(self):
        return self.get_stat(RuneInstance.STAT_SPD, False)

    def get_cri_rate(self):
        return self.get_stat(RuneInstance.STAT_CRIT_RATE_PCT, False)

    def get_cri_dmg(self):
        return self.get_stat(RuneInstance.STAT_CRIT_DMG_PCT, False)

    def get_res(self):
        return self.get_stat(RuneInstance.STAT_RESIST_PCT, False)

    def get_acc(self):
        return self.get_stat(RuneInstance.STAT_ACCURACY_PCT, False)

    def get_innate_stat_title(self):
        if self.innate_stat is not None:
            return self.INNATE_STAT_TITLES[self.innate_stat]
        else:
            return ''

    def get_efficiency(self):
        # https://www.youtube.com/watch?v=SBWeptNNbYc
        if self.stars >= 5:
            running_sum = 0

            if self.innate_stat in self.SUBSTAT_MAX_VALUES:
                running_sum += self.innate_stat_value / self.SUBSTAT_MAX_VALUES[self.innate_stat]

            if self.substat_1 in self.SUBSTAT_MAX_VALUES:
                running_sum += self.substat_1_value / self.SUBSTAT_MAX_VALUES[self.substat_1]

            if self.substat_2 in self.SUBSTAT_MAX_VALUES:
                running_sum += self.substat_2_value / self.SUBSTAT_MAX_VALUES[self.substat_2]

            if self.substat_3 in self.SUBSTAT_MAX_VALUES:
                running_sum += self.substat_3_value / self.SUBSTAT_MAX_VALUES[self.substat_3]

            if self.substat_4 in self.SUBSTAT_MAX_VALUES:
                running_sum += self.substat_4_value / self.SUBSTAT_MAX_VALUES[self.substat_4]

            running_sum += 1 if self.stars == 6 else 0.85

            return running_sum / 2.8 * 100
        else:
            return None

    def update_fields(self):
        # Set flags for filtering
        rune_stat_types = [self.main_stat, self.innate_stat, self.substat_1, self.substat_2, self.substat_3, self.substat_4]
        self.has_hp = any([i for i in rune_stat_types if i in [self.STAT_HP, self.STAT_HP_PCT]])
        self.has_atk = any([i for i in rune_stat_types if i in [self.STAT_ATK, self.STAT_ATK_PCT]])
        self.has_def = any([i for i in rune_stat_types if i in [self.STAT_DEF, self.STAT_DEF_PCT]])
        self.has_crit_rate = self.STAT_CRIT_RATE_PCT in rune_stat_types
        self.has_crit_dmg = self.STAT_CRIT_DMG_PCT in rune_stat_types
        self.has_speed = self.STAT_SPD in rune_stat_types
        self.has_resist = self.STAT_RESIST_PCT in rune_stat_types
        self.has_accuracy = self.STAT_ACCURACY_PCT in rune_stat_types

        self.quality = len(filter(None, [self.substat_1, self.substat_2, self.substat_3, self.substat_4]))
        self.efficiency = self.get_efficiency()

        # Clean up values that don't have a stat type picked
        if self.innate_stat is None:
            self.innate_stat_value = None
        if self.substat_1 is None:
            self.substat_1_value = None
        if self.substat_2 is None:
            self.substat_2_value = None
        if self.substat_3 is None:
            self.substat_3_value = None
        if self.substat_4 is None:
            self.substat_4_value = None

        # Check no other runes are in this slot
        if self.assigned_to:
            for rune in RuneInstance.objects.filter(assigned_to=self.assigned_to, slot=self.slot):
                rune.assigned_to = None
                rune.save()

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check slot, level, etc for valid ranges
        if self.slot is not None:
            if self.slot < 1 or self.slot > 6:
                raise ValidationError({
                    'slot': ValidationError(
                        'Slot must be 1 through 6.',
                        code='invalid_rune_slot',
                    )
                })
            # Do slot vs stat check
            if self.main_stat not in RuneInstance.get_valid_stats_for_slot(self.slot):
                raise ValidationError({
                    'main_stat': ValidationError(
                        'Unacceptable stat for slot %(slot)s. Must be %(valid_stats)s.',
                        params={
                            'slot': self.slot,
                            'valid_stats': ', '.join(RuneInstance.get_valid_stats_for_slot(self.slot).values())
                        },
                        code='invalid_rune_main_stat'
                    ),
                })

        if self.level is not None and self.level < 0 or self.level > 15:
            raise ValidationError({
                'level': ValidationError(
                    'Level must be 0 through 15.',
                    code='invalid_rune_level',
                )
            })

        if self.stars is not None and self.stars < 1 or self.stars > 6:
            raise ValidationError({
                'stars': ValidationError(
                    'Stars must be between 1 and 6.',
                    code='invalid_rune_stars',
                )
            })

        # Check that the same stat type was not used multiple times
        from operator import is_not
        from functools import partial
        stat_list = filter(partial(is_not, None), [self.main_stat, self.innate_stat, self.substat_1, self.substat_2, self.substat_3, self.substat_4])
        if len(stat_list) != len(set(stat_list)):
            raise ValidationError(
                'All stats and substats must be unique.',
                code='duplicate_stats'
            )

        # Check if stat type was specified that it has value > 0
        if self.main_stat_value is None or self.main_stat_value <= 0:
            raise ValidationError({
                'main_stat_value': ValidationError(
                    'Must provide a value greater than 0.',
                    code='invalid_rune_main_stat_value'
                ),
            })

        if self.innate_stat is not None and (self.innate_stat_value is None or self.innate_stat_value <= 0):
            raise ValidationError({
                'innate_stat_value': ValidationError(
                    'Must be greater than 0.',
                    code='invalid_rune_innate_stat_value'
                ),
            })

        if self.substat_1 is not None and (self.substat_1_value is None or self.substat_1_value <= 0):
            raise ValidationError({
                'substat_1_value': ValidationError(
                    'Must be greater than 0.',
                    code='invalid_rune_substat_1_value'
                ),
            })

        if self.substat_2 is not None and (self.substat_2_value is None or self.substat_2_value <= 0):
            raise ValidationError({
                'substat_2_value': ValidationError(
                    'Must be greater than 0.',
                    code='invalid_rune_substat_2_value'
                ),
            })

        if self.substat_3 is not None and (self.substat_3_value is None or self.substat_3_value <= 0):
            raise ValidationError({
                'substat_3_value': ValidationError(
                    'Must be greater than 0.',
                    code='invalid_rune_substat_3_value'
                ),
            })

        if self.substat_4 is not None and (self.substat_4_value is None or self.substat_4_value <= 0):
            raise ValidationError({
                'substat_4_value': ValidationError(
                    'Must be greater than 0.',
                    code='invalid_rune_substat_4_value'
                ),
            })

        # Check that monster rune is assigned to does not already have rune in that slot
        if self.assigned_to is not None and self.assigned_to.runeinstance_set.filter(slot=self.slot).exclude(pk=self.pk).count() > 0:
            raise ValidationError(
                'Monster already has rune in slot %(slot)s. Either pick a different slot or do not assign to the monster yet.',
                params={
                    'slot': self.slot,
                },
                code='slot_occupied'
            )

        super(RuneInstance, self).clean()

    def save(self, *args, **kwargs):
        self.update_fields()
        super(RuneInstance, self).save(*args, **kwargs)

        # Trigger stat calc update on the assigned monster
        if self.assigned_to:
            self.assigned_to.save()

    def __unicode__(self):
        return self.get_innate_stat_title() + ' ' + self.get_type_display() + ' ' + 'Rune'

    class Meta:
        ordering = ['slot', 'type', 'level', 'quality']


class TeamGroup(models.Model):
    owner = models.ForeignKey(Summoner)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=30)

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return self.name


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    group = models.ForeignKey(TeamGroup)
    name = models.CharField(max_length=30)
    favorite = models.BooleanField(default=False, blank=True)
    description = models.TextField(null=True, blank=True, help_text=mark_safe('<a href="https://daringfireball.net/projects/markdown/syntax" target="_blank">Markdown syntax</a> enabled'))
    leader = models.ForeignKey('MonsterInstance', related_name='team_leader', null=True, blank=True)
    roster = models.ManyToManyField('MonsterInstance', blank=True)

    class Meta:
        ordering = ['name']

    def owner(self):
        return self.group.owner

    def __unicode__(self):
        return self.name


# Game event calendar stuff
class GameEvent(models.Model):
    TYPE_ELEMENT_DUNGEON = 1
    TYPE_SPECIAL_EVENT = 2

    EVENT_TYPES = (
        (TYPE_ELEMENT_DUNGEON, "Elemental Dungeon"),
        (TYPE_SPECIAL_EVENT, "Special Event"),
    )

    DAY_MONDAY = 0
    DAY_TUESDAY = 1
    DAY_WEDNESDAY = 2
    DAY_THURSDAY = 3
    DAY_FRIDAY = 4
    DAY_SATURDAY = 5
    DAY_SUNDAY = 6

    DAYS_OF_WEEK = (
        (DAY_SUNDAY, 'Sunday'),
        (DAY_MONDAY, 'Monday'),
        (DAY_TUESDAY, 'Tuesday'),
        (DAY_WEDNESDAY, 'Wednesday'),
        (DAY_THURSDAY, 'Thursday'),
        (DAY_FRIDAY, 'Friday'),
        (DAY_SATURDAY, 'Saturday'),
    )

    name = models.CharField(max_length=100)
    type = models.IntegerField(choices=EVENT_TYPES)
    element_affinity = models.CharField(choices=Monster.ELEMENT_CHOICES, max_length=10, null=True)
    description = models.TextField(null=True, blank=True)
    link = models.TextField(null=True, blank=True)
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    timezone = TimeZoneField(default='America/Los_Angeles')
    all_day = models.BooleanField()

    def is_active(self):
        import datetime

        if self.day_of_week:
            return datetime.datetime.today().weekday() == self.day_of_week

    def __unicode__(self):
        return self.name
