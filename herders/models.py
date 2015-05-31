import uuid

from django.db import models
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.contrib.staticfiles.templatetags.staticfiles import static

from timezone_field import TimeZoneField


class Summoner(models.Model):
    user = models.OneToOneField(User)
    summoner_name = models.CharField(max_length=256)
    global_server = models.BooleanField(default=True)
    public = models.BooleanField(default=False)
    timezone = TimeZoneField(default='America/Los_Angeles')
    notes = models.TextField(blank=True)
    rep_monster = models.ForeignKey('MonsterInstance', null=True, blank=True)
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
    element = models.CharField(max_length=6, choices=ELEMENT_CHOICES, default=ELEMENT_FIRE)
    archetype = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_ATTACK)
    base_stars = models.IntegerField(choices=STAR_CHOICES)
    can_awaken = models.BooleanField(default=True)
    is_awakened = models.BooleanField(default=False)
    awakens_from = models.ForeignKey('self', null=True, blank=True)
    awaken_ele_mats_low = models.IntegerField(null=True, blank=True)
    awaken_ele_mats_mid = models.IntegerField(null=True, blank=True)
    awaken_ele_mats_high = models.IntegerField(null=True, blank=True)
    awaken_magic_mats_low = models.IntegerField(null=True, blank=True)
    awaken_magic_mats_mid = models.IntegerField(null=True, blank=True)
    awaken_magic_mats_high = models.IntegerField(null=True, blank=True)
    fusion_food = models.BooleanField(default=False)

    def image_filename(self):
        # There are special cases where a monster is awakened but has no base monster. If that is the case the filename
        # for awakened is <uniqueName>_<element>.png instead of normal awakened name
        if self.is_awakened and self.awakens_from is not None:
            return self.awakens_from.image_filename().replace('.png', '_awakened.png')
        else:
            return self.name.lower().replace(' ', '_') + '_' + str(self.element) + '.png'

    def image_url(self):
        return mark_safe('<img src="%s" height="42" width="42"/>' % static('herders/images/monsters/' + self.image_filename()))

    def awakens_to(self):
        return self.monster_set.get()

    class Meta:
        ordering = ['name', 'element']

    def __unicode__(self):
        return self.name + ' (' + self.element.capitalize() + ')'


class MonsterSkill(models.Model):
    monster = models.ForeignKey('Monster')
    name = models.CharField(max_length=40)
    description = models.TextField()
    skill_number = models.IntegerField()
    max_level = models.IntegerField()
    icon_path = models.CharField(max_length=100)


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
    skill_1_level = models.IntegerField(null=True, blank=True)
    skill_2_level = models.IntegerField(null=True, blank=True)
    skill_3_level = models.IntegerField(null=True, blank=True)
    skill_4_level = models.IntegerField(null=True, blank=True)
    fodder = models.BooleanField(default=False)
    fodder_for = models.ForeignKey('self', null=True, blank=True)
    priority = models.IntegerField(choices=PRIORITY_CHOICES, default=PRIORITY_MED)
    notes = models.TextField(null=True, blank=True)

    def max_level_from_stars(self):
        return 10 + self.stars * 5

    def is_max_level(self):
        return self.level == self.max_level_from_stars()

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.level > 40 or self.level < 1:
            raise ValidationError(
                'Level out of range (Valid range %(min)s-%(max)s)',
                params={'min': 1, 'max': 40},
                code='invalid_level'
            )

        if self.level > 10 + self.stars * 5:
            raise ValidationError(
                'Level exceeds max for given star rating (Max: %(value)s)',
                params={'value': self.max_level_from_stars()},
                code='invalid_level'
            )

        if self.stars > 6 or self.stars < 1:
            raise ValidationError(
                'Star rating out of range',
                code='invalid_stars'
            )
        super(MonsterInstance, self).clean()

    def __unicode__(self):
        return str(self.owner) + \
            ' (' + str(self.owner.summoner_name) + '), ' + \
            str(self.monster) + ', ' + str(self.stars) + '*, lvl ' + str(self.level)

    class Meta:
        ordering = ['-stars', '-level', '-priority', 'monster__name']
