from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db import models
from django.utils.safestring import mark_safe

from . import base
from .items import GameItem, ItemQuantity
from .monsters import Monster


class Skill(models.Model):
    com2us_id = models.IntegerField(blank=True, null=True, help_text='ID given in game data files')
    name = models.CharField(max_length=60)
    description = models.TextField()
    slot = models.IntegerField(default=1, help_text='Which button position the skill is in during battle')
    skill_effect = models.ManyToManyField('SkillEffect', blank=True)
    effect = models.ManyToManyField('SkillEffect', through='SkillEffectDetail', blank=True, related_name='effect', help_text='Detailed skill effect information')
    cooltime = models.IntegerField(null=True, blank=True, help_text='Number of turns until skill can be used again')
    hits = models.IntegerField(default=1, help_text='Number of times this skill hits an enemy')
    aoe = models.BooleanField(default=False, help_text='Skill affects all enemies or allies')
    passive = models.BooleanField(default=False, help_text='Skill activates automatically')
    max_level = models.IntegerField()
    icon_filename = models.CharField(max_length=100, null=True, blank=True)
    multiplier_formula = models.TextField(null=True, blank=True, help_text='Parsed multiplier formula')
    multiplier_formula_raw = models.CharField(max_length=150, null=True, blank=True, help_text='Multiplier formula given in game data files')
    scaling_stats = models.ManyToManyField('ScalingStat', blank=True, help_text='Monster stats which this skill scales on')

    # Depreciated fields - to be removed
    level_progress_description = models.TextField(null=True, blank=True, help_text='Description of bonus each skill level')

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


class SkillUpgrade(models.Model):
    UPGRADE_EFFECT_RATE = 0
    UPGRADE_DAMAGE = 1
    UPGRADE_RECOVERY = 2
    UPGRADE_COOLTIME = 3
    UPGRADE_SHIELD = 4
    UPGRADE_ATK_BAR = 5
    UPGRADE_EFFECT_DURATION = 6

    UPGRADE_CHOICES = (
        (UPGRADE_EFFECT_RATE, 'Effect Rate +{0}%'),
        (UPGRADE_DAMAGE, 'Damage +{0}%'),
        (UPGRADE_RECOVERY, 'Recovery +{0}%'),
        (UPGRADE_COOLTIME, 'Cooltime Turn -{0}'),
        (UPGRADE_SHIELD, 'Shield +{0}%'),
        (UPGRADE_ATK_BAR, 'Attack Bar Recovery +{0}%'),
        (UPGRADE_EFFECT_DURATION, 'Harmful Effect Rate +{0} Turns'),
    )

    # Mappings from com2us' API data to model defined values
    COM2US_UPGRADE_MAP = {
        'DR': UPGRADE_EFFECT_RATE,
        'AT': UPGRADE_DAMAGE,
        'AT1': UPGRADE_DAMAGE,
        'HE': UPGRADE_RECOVERY,
        'TN': UPGRADE_COOLTIME,
        'SD': UPGRADE_SHIELD,
        'SD1': UPGRADE_SHIELD,
        'GA': UPGRADE_ATK_BAR,
        'DT': UPGRADE_EFFECT_DURATION,
    }

    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='upgrades')
    level = models.IntegerField()
    effect = models.IntegerField(choices=UPGRADE_CHOICES)
    amount = models.IntegerField()

    class Meta:
        ordering = ('level', )

    def __str__(self):
        return f'{self.get_effect_display().format(self.amount)}'


class LeaderSkill(models.Model):
    # TODO: Replace these with base.Stats references
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

    # Mappings from com2us' API data to model defined values
    COM2US_STAT_MAP = {
        1: ATTRIBUTE_HP,
        2: ATTRIBUTE_ATK,
        3: ATTRIBUTE_DEF,
        4: ATTRIBUTE_SPD,
        5: ATTRIBUTE_CRIT_RATE,
        6: ATTRIBUTE_CRIT_DMG,
        7: ATTRIBUTE_RESIST,
        8: ATTRIBUTE_ACCURACY,
    }

    COM2US_AREA_MAP = {
        0: AREA_GENERAL,
        1: AREA_ARENA,
        2: AREA_DUNGEON,
        5: AREA_GUILD,
    }

    attribute = models.IntegerField(choices=ATTRIBUTE_CHOICES, help_text='Monster stat which is granted the bonus')
    amount = models.IntegerField(help_text='Amount of bonus granted')
    area = models.IntegerField(choices=AREA_CHOICES, default=AREA_GENERAL, help_text='Where this leader skill has an effect')
    element = models.CharField(max_length=6, null=True, blank=True, choices=base.Elements.ELEMENT_CHOICES, help_text='Element of monster which this leader skill applies to')

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
            area = f' with the {self.get_element_display()} element'
        else:
            if self.area == self.AREA_ARENA:
                area = ' in the Arena'
            elif self.area == self.AREA_DUNGEON:
                area = ' in the Dungeons'
            elif self.area == self.AREA_GUILD:
                area = ' in Guild content'
            else:
                area = ''

        return f'Increases {self.get_attribute_display()} of ally monsters{area} by {self.amount}%'

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
    craft_materials = models.ManyToManyField(
        GameItem,
        through='HomunculusSkillCraftCost',
        help_text='Crafting materials required to purchase'
    )
    prerequisites = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='homunculus_prereq',
        help_text='Skills which must be acquired first'
    )

    def __str__(self):
        return '{} ({})'.format(self.skill, self.skill.com2us_id)


class HomunculusSkillCraftCost(ItemQuantity):
    skill = models.ForeignKey(HomunculusSkill, on_delete=models.CASCADE)
