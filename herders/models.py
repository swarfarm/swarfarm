import uuid
from collections import OrderedDict

from django.db import models
from django.contrib.auth.models import User
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
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
    )

    name = models.CharField(max_length=40)
    image_filename = models.CharField(max_length=250, null=True, blank=True)
    element = models.CharField(max_length=6, choices=ELEMENT_CHOICES, default=ELEMENT_FIRE)
    archetype = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_ATTACK)
    base_stars = models.IntegerField(choices=STAR_CHOICES)
    obtainable = models.BooleanField(default=True)
    can_awaken = models.BooleanField(default=True)
    is_awakened = models.BooleanField(default=False)
    awaken_bonus = models.TextField(blank=True)
    skills = models.ManyToManyField('MonsterSkill', blank=True)
    leader_skill = models.ForeignKey('MonsterLeaderSkill', null=True, blank=True)
    base_hp = models.IntegerField(null=True, blank=True)
    base_attack = models.IntegerField(null=True, blank=True)
    base_defense = models.IntegerField(null=True, blank=True)
    speed = models.IntegerField(null=True, blank=True)
    crit_rate = models.IntegerField(null=True, blank=True)
    crit_damage = models.IntegerField(null=True, blank=True)
    resistance = models.IntegerField(null=True, blank=True)
    accuracy = models.IntegerField(null=True, blank=True)
    awakens_from = models.ForeignKey('self', null=True, blank=True, related_name='+')
    awakens_to = models.ForeignKey('self', null=True, blank=True, related_name='+')
    awaken_ele_mats_low = models.IntegerField(null=True, blank=True)
    awaken_ele_mats_mid = models.IntegerField(null=True, blank=True)
    awaken_ele_mats_high = models.IntegerField(null=True, blank=True)
    awaken_magic_mats_low = models.IntegerField(null=True, blank=True)
    awaken_magic_mats_mid = models.IntegerField(null=True, blank=True)
    awaken_magic_mats_high = models.IntegerField(null=True, blank=True)
    source = models.ManyToManyField('MonsterSource', blank=True)
    fusion_food = models.BooleanField(default=False)
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

    def get_awakening_materials(self):
        if self.is_awakened and self.awakens_from is not None:
            return self.awakens_from.get_awakening_materials()
        else:
            mats = OrderedDict()
            mats['magic'] = OrderedDict()
            mats[self.element] = OrderedDict()

            if self.awaken_magic_mats_high:
                mats['magic']['high'] = self.awaken_magic_mats_high

            if self.awaken_magic_mats_mid:
                mats['magic']['mid'] = self.awaken_magic_mats_mid

            if self.awaken_magic_mats_low:
                mats['magic']['low'] = self.awaken_magic_mats_low

            if self.awaken_ele_mats_high:
                mats[self.element]['high'] = self.awaken_ele_mats_high

            if self.awaken_ele_mats_mid:
                mats[self.element]['mid'] = self.awaken_ele_mats_mid

            if self.awaken_ele_mats_low:
                mats[self.element]['low'] = self.awaken_ele_mats_low

            return mats

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

    def skill_ups_to_max(self):
        if self.skills is not None:
            skill_list = self.skills.values_list('max_level', flat=True)
            return sum(skill_list) - len(skill_list)
        else:
            return None

    def all_skill_effects(self):
        return MonsterSkillEffect.objects.filter(pk__in=self.skills.exclude(skill_effect=None).values_list('skill_effect', flat=True))

    def farmable(self):
        if self.is_awakened and self.awakens_from is not None:
            return self.awakens_from.source.filter(farmable_source=True).count() > 0
        else:
            return self.source.filter(farmable_source=True).count() > 0

    def save(self, *args, **kwargs):
        # Update image filename on save.
        if self.is_awakened and self.awakens_from is not None:
            self.image_filename = self.awakens_from.image_filename.replace('.png', '_awakened.png')
        else:
            self.image_filename = self.name.lower().replace(' ', '_') + '_' + str(self.element) + '.png'

        # Generate summonerswar.co URL if possible
        if self.can_awaken and self.archetype is not self.TYPE_MATERIAL and (self.summonerswar_co_url is None or self.summonerswar_co_url == ''):
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

        super(Monster, self).save(*args, **kwargs)

    class Meta:
        ordering = ['name', 'element']

    def __unicode__(self):
        if self.is_awakened:
            return self.name
        else:
            return self.name + ' (' + self.element.capitalize() + ')'


class MonsterSkill(models.Model):
    name = models.CharField(max_length=40)
    description = models.TextField()
    slot = models.IntegerField(default=1)
    skill_effect = models.ManyToManyField('MonsterSkillEffect', blank=True)
    passive = models.BooleanField(default=False)
    max_level = models.IntegerField()
    level_progress_description = models.TextField(null=True, blank=True)
    icon_filename = models.CharField(max_length=100, null=True, blank=True)

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

    attribute = models.IntegerField(choices=ATTRIBUTE_CHOICES)
    amount = models.IntegerField()
    dungeon_skill = models.BooleanField(default=False)
    element_skill = models.BooleanField(default=False)
    element = models.CharField(max_length=6, null=True, blank=True, choices=Monster.ELEMENT_CHOICES)
    arena_skill = models.BooleanField(default=False)
    guild_skill = models.BooleanField(default=False)

    def skill_string(self):
        if self.dungeon_skill:
            condition = 'in the Dungeons '
        elif self.arena_skill:
            condition = 'in the Arena '
        elif self.guild_skill:
            condition = 'in the Guild Battles '
        elif self.element_skill:
            condition = 'with {} attribute '.format(self.get_element_display())
        else:
            condition = ''

        return "Increase the {0} of ally monsters {1}by {2}%".format(self.get_attribute_display(), condition, self.amount)

    def icon_filename(self):
        if self.dungeon_skill:
            suffix = '_Dungeon'
        elif self.arena_skill:
            suffix = '_Arena'
        elif self.guild_skill:
            suffix = '_Guild'
        elif self.element_skill:
            suffix = '_{}'.format(self.get_element_display())
        else:
            suffix = ''

        return 'leader_skill_{0}{1}.png'.format(self.get_attribute_display().replace(' ', '_'), suffix)

    def image_url(self):
        return mark_safe('<img src="{}" height="42" width="42"/>'.format(
            static('herders/images/skills/leader/' + self.icon_filename())
        ))

    def __unicode__(self):
        if self.dungeon_skill:
            condition = ' Dungeon'
        elif self.arena_skill:
            condition = ' Arena'
        elif self.guild_skill:
            condition = ' Guild'
        elif self.element_skill:
            condition = ' ' + self.get_element_display()
        else:
            condition = ''

        return self.get_attribute_display() + ' ' + str(self.amount) + '%' + condition

    class Meta:
        ordering = ['attribute', 'amount', 'element']


class MonsterSkillEffect(models.Model):
    is_buff = models.BooleanField(default=True)
    name = models.CharField(max_length=40)
    description = models.TextField()
    icon_filename = models.CharField(max_length=100, null=True, blank=True)

    def image_url(self):
        if self.icon_filename:
            return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/buffs/' + self.icon_filename))
        else:
            return 'No Image'

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ['-is_buff', 'name']


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
        storage['magic']['high'] = self.storage_magic_high
        storage['magic']['mid'] = self.storage_magic_mid
        storage['magic']['low'] = self.storage_magic_low
        storage['fire'] = OrderedDict()
        storage['fire']['high'] = self.storage_fire_high
        storage['fire']['mid'] = self.storage_fire_mid
        storage['fire']['low'] = self.storage_fire_low
        storage['water'] = OrderedDict()
        storage['water']['high'] = self.storage_water_high
        storage['water']['mid'] = self.storage_water_mid
        storage['water']['low'] = self.storage_water_low
        storage['wind'] = OrderedDict()
        storage['wind']['high'] = self.storage_wind_high
        storage['wind']['mid'] = self.storage_wind_mid
        storage['wind']['low'] = self.storage_wind_low
        storage['light'] = OrderedDict()
        storage['light']['high'] = self.storage_light_high
        storage['light']['mid'] = self.storage_light_mid
        storage['light']['low'] = self.storage_light_low
        storage['dark'] = OrderedDict()
        storage['dark']['high'] = self.storage_dark_high
        storage['dark']['mid'] = self.storage_dark_mid
        storage['dark']['low'] = self.storage_dark_low

        return storage

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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('Summoner')
    monster = models.ForeignKey('Monster')
    stars = models.IntegerField()
    level = models.IntegerField()
    skill_1_level = models.IntegerField(blank=True, default=1)
    skill_2_level = models.IntegerField(blank=True, default=1)
    skill_3_level = models.IntegerField(blank=True, default=1)
    skill_4_level = models.IntegerField(blank=True, default=1)
    fodder = models.BooleanField(default=False)
    in_storage = models.BooleanField(default=False)
    ignore_for_fusion = models.BooleanField(default=False)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_MED)
    notes = models.TextField(null=True, blank=True)

    def is_max_level(self):
        return self.level == self.monster.max_level_from_stars(self.stars)

    def max_level_from_stars(self):
        return self.monster.max_level_from_stars(self.stars)

    def skill_ups_to_max(self):
        skill_ups_remaining = self.monster.skill_ups_to_max()
        skill_levels = [self.skill_1_level, self.skill_2_level, self.skill_3_level, self.skill_4_level]

        for idx in range(0, self.monster.skills.count()):
            skill_ups_remaining -= skill_levels[idx] - 1

        return skill_ups_remaining

    # Stat callables. Base = monster's own stat. Rune = amount gained from runes. Bare stat is combined
    def base_hp(self):
        return self.monster.actual_hp(self.stars, self.level)

    def rune_hp(self):
        return 0

    def hp(self):
        return self.base_hp() + self.rune_hp()

    def base_attack(self):
        return self.monster.actual_attack(self.stars, self.level)

    def rune_attack(self):
        return 0

    def attack(self):
        return self.base_attack() + self.rune_attack()

    def base_defense(self):
        return self.monster.actual_defense(self.stars, self.level)

    def rune_defense(self):
        return 0

    def defense(self):
        return self.base_defense() + self.rune_defense()

    def base_speed(self):
        return self.monster.speed

    def rune_speed(self):
        return 0

    def speed(self):
        return self.base_speed() + self.rune_speed()

    def base_crit_rate(self):
        return self.monster.crit_rate

    def rune_crit_rate(self):
        return 0

    def crit_rate(self):
        return self.base_crit_rate() + self.rune_crit_rate()

    def base_crit_damage(self):
        return self.monster.crit_damage

    def rune_crit_damage(self):
        return 0

    def crit_damage(self):
        return self.base_crit_damage() + self.rune_crit_damage()

    def base_resistance(self):
        return self.monster.resistance

    def rune_resistance(self):
        return 0

    def resistance(self):
        return self.base_resistance() + self.rune_resistance()

    def base_accuracy(self):
        return self.monster.accuracy

    def rune_accuracy(self):
        return 0

    def accuracy(self):
        return self.base_accuracy() + self.rune_accuracy()

    def clean(self):
        from django.core.exceptions import ValidationError, ObjectDoesNotExist

        if self.level > 40 or self.level < 1:
            raise ValidationError(
                'Level out of range (Valid range %(min)s-%(max)s)',
                params={'min': 1, 'max': 40},
                code='invalid_level'
            )

        if self.level > 10 + self.stars * 5:
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

        if self.stars > 6 or self.stars < min_stars:
            raise ValidationError(
                'Star rating out of range (%(min)s to %(max)s)',
                params={'min': min_stars, 'max': 6},
                code='invalid_stars'
            )
        super(MonsterInstance, self).clean()

    def __unicode__(self):
        return str(self.monster) + ', ' + str(self.stars) + '*, Lvl ' + str(self.level)

    class Meta:
        ordering = ['-stars', '-level', '-priority', 'monster__name']


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

    INNATE_STAT_CHOICES = (
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

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.IntegerField(choices=TYPE_CHOICES)
    owner = models.ForeignKey(Summoner)
    monster = models.ForeignKey('MonsterInstance', null=True, blank=True)
    stars = models.IntegerField()
    level = models.IntegerField()
    slot = models.IntegerField()
    main_stat = models.IntegerField(choices=STAT_CHOICES)
    main_stat_value = models.IntegerField(default=0)
    innate_stat = models.IntegerField(choices=INNATE_STAT_CHOICES, null=True, blank=True)
    innate_stat_value = models.IntegerField(null=True, blank=True)
    substat_1 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_1_value = models.IntegerField(null=True, blank=True)
    substat_2 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_2_value = models.IntegerField(null=True, blank=True)
    substat_3 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_3_value = models.IntegerField(null=True, blank=True)
    substat_4 = models.IntegerField(choices=STAT_CHOICES, null=True, blank=True)
    substat_4_value = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.TYPE_CHOICES[self.type - 1][1] + ', Slot ' + str(self.slot) + ', ' + str(self.stars) + '*, Lvl ' + str(self.level) + ', +' + str(self.main_stat_value) + ' ' + self.STAT_CHOICES[self.main_stat - 1][1]


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
    description = models.TextField(null=True, blank=True)
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
