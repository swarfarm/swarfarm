from collections import OrderedDict

from django.db import models
from django.db.models import Q
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.contrib.staticfiles.templatetags.staticfiles import static


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
        family = Monster.objects.filter(com2us_id=self.com2us_id, obtainable=True).order_by('element')

        return [
            {
                'unawakened': family.filter(element=Monster.ELEMENT_FIRE, is_awakened=False).first(),
                'awakened': family.filter(element=Monster.ELEMENT_FIRE, is_awakened=True).first(),
            },
            {
                'unawakened': family.filter(element=Monster.ELEMENT_WATER, is_awakened=False).first(),
                'awakened': family.filter(element=Monster.ELEMENT_WATER, is_awakened=True).first(),
            },
            {
                'unawakened': family.filter(element=Monster.ELEMENT_WIND, is_awakened=False).first(),
                'awakened': family.filter(element=Monster.ELEMENT_WIND, is_awakened=True).first(),
            },
            {
                'unawakened': family.filter(element=Monster.ELEMENT_LIGHT, is_awakened=False).first(),
                'awakened': family.filter(element=Monster.ELEMENT_LIGHT, is_awakened=True).first(),
            },
            {
                'unawakened': family.filter(element=Monster.ELEMENT_DARK, is_awakened=False).first(),
                'awakened': family.filter(element=Monster.ELEMENT_DARK, is_awakened=True).first(),
            },
        ]

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
    hits = models.IntegerField(default=1)
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
    chance = models.IntegerField(null=True, blank=True, help_text='Chance of effect occuring per hit')
    on_crit = models.BooleanField(default=False)
    on_death = models.BooleanField(default=False)
    random = models.BooleanField(default=False, help_text='Skill effect applies randomly to the target')
    quantity = models.IntegerField(null=True, blank=True, help_text='Number of items this effect affects on the target')
    all = models.BooleanField(default=False, help_text='This effect affects all items on the target')
    note = models.TextField(blank=True, null=True, help_text="Explain anything else that doesn't fit in other fields")


class MonsterSkillScalingStat(models.Model):
    stat = models.CharField(max_length=20)

    def __unicode__(self):
        return self.stat


class MonsterSkillScalesWith(models.Model):
    scalingstat = models.ForeignKey(MonsterSkillScalingStat)
    monsterskill = models.ForeignKey(MonsterSkill)
    multiplier = models.FloatField(blank=True, null=True)


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

