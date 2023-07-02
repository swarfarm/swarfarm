from math import floor

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from . import base


class ArtifactObjectBase(models.Model, base.Quality, base.Archetype, base.Elements, base.Stats):
    SLOT_ELEMENTAL = 1
    SLOT_ARCHETYPE = 2

    SLOT_CHOICES = (
        (SLOT_ELEMENTAL, 'Element'),
        (SLOT_ARCHETYPE, 'Archetype'),
    )

    COM2US_SLOT_MAP = {
        1: SLOT_ELEMENTAL,
        2: SLOT_ARCHETYPE,
    }

    EFFECT_ATK_LOST_HP = 1
    EFFECT_DEF_LOST_HP = 2
    EFFECT_SPD_LOST_HP = 3
    EFFECT_SPD_INABILITY = 4
    EFFECT_ATK = 5
    EFFECT_DEF = 6
    EFFECT_SPD = 7
    EFFECT_CRIT_RATE = 8
    EFFECT_COUNTER_DMG = 9
    EFFECT_COOP_ATTACK_DMG = 10
    EFFECT_BOMB_DMG = 11
    EFFECT_REFLECT_DMG = 12
    EFFECT_CRUSHING_HIT_DMG = 13
    EFFECT_DMG_RECEIVED_INABILITY = 14
    EFFECT_CRIT_DMG_RECEIVED = 15
    EFFECT_LIFE_DRAIN = 16
    EFFECT_HP_REVIVE = 17
    EFFECT_ATB_REVIVE = 18
    EFFECT_DMG_PCT_OF_HP = 19
    EFFECT_DMG_PCT_OF_ATK = 20
    EFFECT_DMG_PCT_OF_DEF = 21
    EFFECT_DMG_PCT_OF_SPD = 22
    EFFECT_DMG_TO_FIRE = 23
    EFFECT_DMG_TO_WATER = 24
    EFFECT_DMG_TO_WIND = 25
    EFFECT_DMG_TO_LIGHT = 26
    EFFECT_DMG_TO_DARK = 27
    EFFECT_DMG_FROM_FIRE = 28
    EFFECT_DMG_FROM_WATER = 29
    EFFECT_DMG_FROM_WIND = 30
    EFFECT_DMG_FROM_LIGHT = 31
    EFFECT_DMG_FROM_DARK = 32
    EFFECT_SK1_CRIT_DMG = 33
    EFFECT_SK2_CRIT_DMG = 34
    EFFECT_SK3_CRIT_DMG = 35
    EFFECT_SK4_CRIT_DMG = 36
    EFFECT_SK1_RECOVERY = 37
    EFFECT_SK2_RECOVERY = 38
    EFFECT_SK3_RECOVERY = 39
    EFFECT_SK1_ACCURACY = 40
    EFFECT_SK2_ACCURACY = 41
    EFFECT_SK3_ACCURACY = 42
    EFFECT_CRIT_DMG_UP_ENEMY_HP_GOOD = 43
    EFFECT_CRIT_DMG_UP_ENEMY_HP_BAD = 44
    EFFECT_CRIT_DMG_SINGLE_TARGET = 45
    EFFECT_COUNTER_AND_COOP_DMG = 46
    EFFECT_ATK_AND_DEF = 47
    EFFECT_SK3_AND_SK4_CRIT_DMG = 48
    EFFECT_1ST_ATK_CRIT_DMG = 49


    EFFECT_CHOICES = (
        (EFFECT_ATK_LOST_HP, 'ATK+ Proportional to Lost HP'),
        (EFFECT_DEF_LOST_HP, 'DEF+ Proportional to Lost HP'),
        (EFFECT_SPD_LOST_HP, 'SPD+ Proportional to Lost HP'),
        (EFFECT_SPD_INABILITY, 'SPD Under Inability'),
        (EFFECT_ATK, 'ATK Increased'),
        (EFFECT_DEF, 'DEF Increased'),
        (EFFECT_SPD, 'SPD Increased'),
        (EFFECT_CRIT_RATE, 'CRI Rate Increased'),
        (EFFECT_COUNTER_DMG, 'Counterattack Damage Increased'),
        (EFFECT_COOP_ATTACK_DMG, 'Cooperative Attack Damage Increased'),
        (EFFECT_BOMB_DMG, 'Bomb Damage Increased'),
        (EFFECT_REFLECT_DMG, 'Reflected Damage Increased'),
        (EFFECT_CRUSHING_HIT_DMG, 'Crushing Hit Damage Increased'),
        (EFFECT_DMG_RECEIVED_INABILITY, 'Damage Received Under Inability Decreased'),
        (EFFECT_CRIT_DMG_RECEIVED, 'Crit Damage Received Decreased'),
        (EFFECT_LIFE_DRAIN, 'Life Drain Increased'),
        (EFFECT_HP_REVIVE, 'HP When Revived Increased'),
        (EFFECT_ATB_REVIVE, 'Attack Bar When Revived Increased'),
        (EFFECT_DMG_PCT_OF_HP, 'Damage Increased By % of HP'),
        (EFFECT_DMG_PCT_OF_ATK, 'Damage Increased By % of ATK'),
        (EFFECT_DMG_PCT_OF_DEF, 'Damage Increased By % of DEF'),
        (EFFECT_DMG_PCT_OF_SPD, 'Damage Increased By % of SPD'),
        (EFFECT_DMG_TO_FIRE, 'Damage To Fire Increased'),
        (EFFECT_DMG_TO_WATER, 'Damage To Water Increased'),
        (EFFECT_DMG_TO_WIND, 'Damage To Wind Increased'),
        (EFFECT_DMG_TO_LIGHT, 'Damage To Light Increased'),
        (EFFECT_DMG_TO_DARK, 'Damage To Dark Increased'),
        (EFFECT_DMG_FROM_FIRE, 'Damage From Fire Decreased'),
        (EFFECT_DMG_FROM_WATER, 'Damage From Water Decreased'),
        (EFFECT_DMG_FROM_WIND, 'Damage From Wind Decreased'),
        (EFFECT_DMG_FROM_LIGHT, 'Damage From Light Decreased'),
        (EFFECT_DMG_FROM_DARK, 'Damage From Dark Decreased'),
        (EFFECT_SK1_CRIT_DMG, 'Skill 1 CRI Damage Increased'),
        (EFFECT_SK2_CRIT_DMG, 'Skill 2 CRI Damage Increased'),
        (EFFECT_SK3_CRIT_DMG, 'Skill 3 CRI Damage Increased'),
        (EFFECT_SK4_CRIT_DMG, 'Skill 4 CRI Damage Increased'),
        (EFFECT_SK1_RECOVERY, 'Skill 1 Recovery Increased'),
        (EFFECT_SK2_RECOVERY, 'Skill 2 Recovery Increased'),
        (EFFECT_SK3_RECOVERY, 'Skill 3 Recovery Increased'),
        (EFFECT_SK1_ACCURACY, 'Skill 1 Accuracy Increased'),
        (EFFECT_SK2_ACCURACY, 'Skill 2 Accuracy Increased'),
        (EFFECT_SK3_ACCURACY, 'Skill 3 Accuracy Increased'),
        (EFFECT_CRIT_DMG_UP_ENEMY_HP_GOOD, "CRIT DMG+ up to N% as the enemy's HP condition is good"),
        (EFFECT_CRIT_DMG_UP_ENEMY_HP_BAD, "CRIT DMG+ up to N% as the enemy's HP condition is bad"),
        (EFFECT_CRIT_DMG_SINGLE_TARGET, "Single-target skill CRIT DMG +%"),
        (EFFECT_COUNTER_AND_COOP_DMG, "Counterattack and Cooperative Attack Damage Increased"),
        (EFFECT_ATK_AND_DEF, "ATK and DEF Increased"),
        (EFFECT_SK3_AND_SK4_CRIT_DMG, "Skill 3 and Skill 4 CRI Damage Increased"),
        (EFFECT_1ST_ATK_CRIT_DMG, "First Attack CRI Damage Increased"),
    )

    EFFECT_STRINGS = {
        EFFECT_ATK_LOST_HP: 'ATK+ Proportional to Lost HP up to {}%',
        EFFECT_DEF_LOST_HP: 'DEF+ Proportional to Lost HP up to {}%',
        EFFECT_SPD_LOST_HP: 'SPD+ Proportional to Lost HP up to {}%',
        EFFECT_SPD_INABILITY: 'SPD Under Inability +{}%',
        EFFECT_ATK: 'ATK Increasing Effect +{}%',
        EFFECT_DEF: 'DEF Increasing Effect +{}%',
        EFFECT_SPD: 'SPD Increasing Effect +{}%',
        EFFECT_CRIT_RATE: 'CRIT Rate Increasing Effect +{}%',
        EFFECT_COUNTER_DMG: 'Damage Dealt by Counterattack +{}%',
        EFFECT_COOP_ATTACK_DMG: 'Damage Dealt by Attacking Together +{}%',
        EFFECT_BOMB_DMG: 'Bomb Damage +{}%',
        EFFECT_REFLECT_DMG: 'Damage Dealt by Reflect DMG +{}%',
        EFFECT_CRUSHING_HIT_DMG: 'Crushing Hit DMG +{}%',
        EFFECT_DMG_RECEIVED_INABILITY: 'Damage Received Under Inability -{}%',
        EFFECT_CRIT_DMG_RECEIVED: 'CRIT DMG Received -{}%',
        EFFECT_LIFE_DRAIN: 'Life Drain +{}%',
        EFFECT_HP_REVIVE: 'HP when Revived +{}%',
        EFFECT_ATB_REVIVE: 'Attack Bar when Revived +{}%',
        EFFECT_DMG_PCT_OF_HP: 'Additional Damage by {}% of HP',
        EFFECT_DMG_PCT_OF_ATK: 'Additional Damage by {}% of ATK',
        EFFECT_DMG_PCT_OF_DEF: 'Additional Damage by {}% of DEF',
        EFFECT_DMG_PCT_OF_SPD: 'Additional Damage by {}% of SPD',
        EFFECT_DMG_TO_FIRE: 'Damage Dealt on Fire +{}%',
        EFFECT_DMG_TO_WATER: 'Damage Dealt on Water +{}%',
        EFFECT_DMG_TO_WIND: 'Damage Dealt on Wind +{}%',
        EFFECT_DMG_TO_LIGHT: 'Damage Dealt on Light +{}%',
        EFFECT_DMG_TO_DARK: 'Damage Dealt on Dark +{}%',
        EFFECT_DMG_FROM_FIRE: 'Damage Received from Fire -{}%',
        EFFECT_DMG_FROM_WATER: 'Damage Received from Water -{}%',
        EFFECT_DMG_FROM_WIND: 'Damage Received from Wind -{}%',
        EFFECT_DMG_FROM_LIGHT: 'Damage Received from Light -{}%',
        EFFECT_DMG_FROM_DARK: 'Damage Received from Dark -{}%',
        EFFECT_SK1_CRIT_DMG: '[Skill 1] CRIT DMG +{}%',
        EFFECT_SK2_CRIT_DMG: '[Skill 2] CRIT DMG +{}%',
        EFFECT_SK3_CRIT_DMG: '[Skill 3] CRIT DMG +{}%',
        EFFECT_SK4_CRIT_DMG: '[Skill 4] CRIT DMG +{}%',
        EFFECT_SK1_RECOVERY: '[Skill 1] Recovery +{}%',
        EFFECT_SK2_RECOVERY: '[Skill 2] Recovery +{}%',
        EFFECT_SK3_RECOVERY: '[Skill 3] Recovery +{}%',
        EFFECT_SK1_ACCURACY: '[Skill 1] Accuracy +{}%',
        EFFECT_SK2_ACCURACY: '[Skill 2] Accuracy +{}%',
        EFFECT_SK3_ACCURACY: '[Skill 3] Accuracy +{}%',
        EFFECT_CRIT_DMG_UP_ENEMY_HP_GOOD: "CRIT DMG+ up to {}% as the enemy's HP condition is good",
        EFFECT_CRIT_DMG_UP_ENEMY_HP_BAD: "CRIT DMG+ up to {}% as the enemy's HP condition is bad",
        EFFECT_CRIT_DMG_SINGLE_TARGET: "Single-target skill CRIT DMG +{}% on your turn",
        EFFECT_COUNTER_AND_COOP_DMG: "Damage Dealt by Counterattack/Attacking Together +{}%",
        EFFECT_ATK_AND_DEF: "ATK/DEF Increasing Effect +{}%",
        EFFECT_SK3_AND_SK4_CRIT_DMG: "[Skill 3/4] CRIT DMG +{}%",
        EFFECT_1ST_ATK_CRIT_DMG: "First Attack CRIT DMG +{}%",
    }

    COM2US_EFFECT_MAP = {
        200: EFFECT_ATK_LOST_HP,
        201: EFFECT_DEF_LOST_HP,
        202: EFFECT_SPD_LOST_HP,
        203: EFFECT_SPD_INABILITY,
        204: EFFECT_ATK,
        205: EFFECT_DEF,
        206: EFFECT_SPD,
        207: EFFECT_CRIT_RATE,
        208: EFFECT_COUNTER_DMG,
        209: EFFECT_COOP_ATTACK_DMG,
        210: EFFECT_BOMB_DMG,
        211: EFFECT_REFLECT_DMG,
        212: EFFECT_CRUSHING_HIT_DMG,
        213: EFFECT_DMG_RECEIVED_INABILITY,
        214: EFFECT_CRIT_DMG_RECEIVED,
        215: EFFECT_LIFE_DRAIN,
        216: EFFECT_HP_REVIVE,
        217: EFFECT_ATB_REVIVE,
        218: EFFECT_DMG_PCT_OF_HP,
        219: EFFECT_DMG_PCT_OF_ATK,
        220: EFFECT_DMG_PCT_OF_DEF,
        221: EFFECT_DMG_PCT_OF_SPD,
        222: EFFECT_CRIT_DMG_UP_ENEMY_HP_GOOD,
        223: EFFECT_CRIT_DMG_UP_ENEMY_HP_BAD,
        224: EFFECT_CRIT_DMG_SINGLE_TARGET,
        225: EFFECT_COUNTER_AND_COOP_DMG,
        226: EFFECT_ATK_AND_DEF,
        300: EFFECT_DMG_TO_FIRE,
        301: EFFECT_DMG_TO_WATER,
        302: EFFECT_DMG_TO_WIND,
        303: EFFECT_DMG_TO_LIGHT,
        304: EFFECT_DMG_TO_DARK,
        305: EFFECT_DMG_FROM_FIRE,
        306: EFFECT_DMG_FROM_WATER,
        307: EFFECT_DMG_FROM_WIND,
        308: EFFECT_DMG_FROM_LIGHT,
        309: EFFECT_DMG_FROM_DARK,
        400: EFFECT_SK1_CRIT_DMG,
        401: EFFECT_SK2_CRIT_DMG,
        402: EFFECT_SK3_CRIT_DMG,
        403: EFFECT_SK4_CRIT_DMG,
        404: EFFECT_SK1_RECOVERY,
        405: EFFECT_SK2_RECOVERY,
        406: EFFECT_SK3_RECOVERY,
        407: EFFECT_SK1_ACCURACY,
        408: EFFECT_SK2_ACCURACY,
        409: EFFECT_SK3_ACCURACY,
        410: EFFECT_SK3_AND_SK4_CRIT_DMG,
        411: EFFECT_1ST_ATK_CRIT_DMG,
    }

    slot = models.IntegerField(db_index=True, choices=SLOT_CHOICES)
    element = models.CharField(db_index=True, max_length=6, choices=base.Elements.NORMAL_ELEMENT_CHOICES, blank=True, null=True)
    archetype = models.CharField(db_index=True, max_length=10, choices=base.Archetype.ARCHETYPE_CHOICES, blank=True, null=True)
    quality = models.IntegerField(default=0, choices=base.Quality.QUALITY_CHOICES)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()

        # Check that element or archetype is defined when that slot is chosen
        if self.slot == self.SLOT_ELEMENTAL:
            self.archetype = None
            if not self.element:
                raise ValidationError({
                    'element': ValidationError(
                        'Element is required for an Elemental slotted artifact.',
                        code='element_required'
                    )
                })
        else:
            self.element = None
            if not self.archetype:
                raise ValidationError({
                    'archetype': ValidationError(
                        'Archetype is required for an Archetype slotted artifact.',
                        code='archetype_required'
                    )
                })


class Artifact(ArtifactObjectBase):
    MAIN_STAT_CHOICES = (
        (ArtifactObjectBase.STAT_HP, 'HP'),
        (ArtifactObjectBase.STAT_ATK, 'ATK'),
        (ArtifactObjectBase.STAT_DEF, 'DEF'),
    )

    COM2US_MAIN_STAT_MAP = {
        100: ArtifactObjectBase.STAT_HP,
        101: ArtifactObjectBase.STAT_ATK,
        102: ArtifactObjectBase.STAT_DEF,
    }

    MAIN_STAT_VALUES = {
        ArtifactObjectBase.STAT_HP: [160, 220, 280, 340, 400, 460, 520, 580, 640, 700, 760, 820, 880, 940, 1000, 1500],
        ArtifactObjectBase.STAT_ATK: [10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 66, 100],
        ArtifactObjectBase.STAT_DEF: [10, 14, 18, 22, 26, 30, 34, 38, 42, 46, 50, 54, 58, 62, 66, 100],
    }

    MAX_NUMBER_OF_EFFECTS = 4

    EFFECT_VALUES = {
        ArtifactObjectBase.EFFECT_SPD: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_BOMB_DMG: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_CRIT_DMG_RECEIVED: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_LIFE_DRAIN: {'min': 5, 'max': 8},
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_HP: {'min': 0.2, 'max': 0.3},
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_ATK: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_DEF: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_SPD: {'min': 25, 'max': 40},
        ArtifactObjectBase.EFFECT_DMG_TO_FIRE: {'min': 3, 'max': 5},
        ArtifactObjectBase.EFFECT_DMG_TO_WATER: {'min': 3, 'max': 5},
        ArtifactObjectBase.EFFECT_DMG_TO_WIND: {'min': 3, 'max': 5},
        ArtifactObjectBase.EFFECT_DMG_TO_LIGHT: {'min': 3, 'max': 5},
        ArtifactObjectBase.EFFECT_DMG_TO_DARK: {'min': 3, 'max': 5},
        ArtifactObjectBase.EFFECT_DMG_FROM_FIRE: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_DMG_FROM_WATER: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_DMG_FROM_WIND: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_DMG_FROM_LIGHT: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_DMG_FROM_DARK: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK1_CRIT_DMG: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK2_CRIT_DMG: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK1_RECOVERY: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK2_RECOVERY: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK3_RECOVERY: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK1_ACCURACY: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK2_ACCURACY: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK3_ACCURACY: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_CRIT_DMG_UP_ENEMY_HP_GOOD: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_CRIT_DMG_UP_ENEMY_HP_BAD: {'min': 8, 'max': 12},
        ArtifactObjectBase.EFFECT_CRIT_DMG_SINGLE_TARGET: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_1ST_ATK_CRIT_DMG: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_COUNTER_AND_COOP_DMG: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_ATK_AND_DEF: {'min': 3, 'max': 5},
        ArtifactObjectBase.EFFECT_SK3_AND_SK4_CRIT_DMG: {'min': 4, 'max': 6},

        # The following effects were removed in patch 6.2.0, but still exist on old artifacts
        ArtifactObjectBase.EFFECT_CRIT_RATE: {'min': 3, 'max': 6},
        ArtifactObjectBase.EFFECT_SPD_INABILITY: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_DMG_RECEIVED_INABILITY: {'min': 1, 'max': 3},
        ArtifactObjectBase.EFFECT_REFLECT_DMG: {'min': 1, 'max': 3},
        ArtifactObjectBase.EFFECT_CRUSHING_HIT_DMG: {'min': 2, 'max': 4},

        # The following effects were removed in patch 8.0.0, but still exist on old artifacts
        ArtifactObjectBase.EFFECT_ATK_LOST_HP: {'min': 9, 'max': 14},
        ArtifactObjectBase.EFFECT_DEF_LOST_HP: {'min': 9, 'max': 14},
        ArtifactObjectBase.EFFECT_SPD_LOST_HP: {'min': 9, 'max': 14},
        ArtifactObjectBase.EFFECT_HP_REVIVE: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_ATB_REVIVE: {'min': 4, 'max': 6},

        # The following effects were combined in patch 8.0.0, but still exist on old artifacts
        ArtifactObjectBase.EFFECT_COUNTER_DMG: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_COOP_ATTACK_DMG: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_ATK: {'min': 3, 'max': 5},
        ArtifactObjectBase.EFFECT_DEF: {'min': 2, 'max': 4},
        ArtifactObjectBase.EFFECT_SK3_CRIT_DMG: {'min': 4, 'max': 6},
        ArtifactObjectBase.EFFECT_SK4_CRIT_DMG: {'min': 4, 'max': 6},

    }

    level = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(15)])
    original_quality = models.IntegerField(choices=ArtifactObjectBase.QUALITY_CHOICES)
    main_stat = models.IntegerField(choices=MAIN_STAT_CHOICES)
    main_stat_value = models.IntegerField(editable=False, blank=True)
    effects = ArrayField(
        models.IntegerField(choices=ArtifactObjectBase.EFFECT_CHOICES, null=True, blank=True),
        size=4,
        default=list,
        blank=True,
        help_text='Bonus effect type'
    )
    effects_value = ArrayField(
        models.FloatField(blank=True, null=True),
        size=4,
        default=list,
        blank=True,
        help_text='Bonus value of this effect'
    )
    effects_upgrade_count = ArrayField(
        models.IntegerField(blank=True, null=True),
        size=4,
        default=list,
        blank=True,
        help_text='Number of upgrades this effect received when leveling artifact'
    )
    effects_reroll_count = ArrayField(
        models.IntegerField(blank=True, null=True),
        size=4,
        default=list,
        blank=True,
        help_text='Number times this upgrades was rerolled with conversion stone'
    )
    efficiency = models.FloatField(blank=True)
    max_efficiency = models.FloatField(blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        level = f'+{self.level} ' if self.level else ''
        return f'{level}{self.get_precise_slot_display()} {self.get_main_stat_display()} Artifact'

    def clean(self):
        super().clean()

        # Effects
        # Check for duplicates
        num_effects = len(self.effects)
        if num_effects != len(set(self.effects)):
            raise ValidationError({
                'effects': ValidationError('All secondary effects must be unique', code='effects_duplicate')
            })

        # Minimum required count based on level
        if num_effects < self.effect_upgrades_received:
            raise ValidationError({
                'effects': ValidationError(
                    'A lv. %(level)s artifact requires at least %(upgrades)s effect(s)',
                    params={
                        'level': self.level,
                        'upgrades': self.effect_upgrades_received,
                    },
                    code='effects_not_enough'
                )
            })

        # Truncate other effect info arrays if longer than number of effects
        self.effects_value = self.effects_value[0:num_effects]
        self.effects_upgrade_count = self.effects_upgrade_count[0:num_effects]
        self.effects_reroll_count = self.effects_reroll_count[0:num_effects]

        # Pad with 0 if too short
        self.effects_value += [0] * (num_effects - len(self.effects_value))
        self.effects_upgrade_count += [0] * (num_effects - len(self.effects_upgrade_count))
        self.effects_reroll_count += [0] * (num_effects - len(self.effects_reroll_count))

        for index, (effect, value) in enumerate(zip(
            self.effects,
            self.effects_value,
        )):
            max_possible_value = self.EFFECT_VALUES[effect]['max'] * (self.effect_upgrades_received + 1)
            min_possible_value = self.EFFECT_VALUES[effect]['min']

            if value is None:
                raise ValidationError({
                    'effects_value': ValidationError(
                        'Effect %(nth)s: Cannot be empty, must be between %(min_val)s and %(max_val)s.',
                        params={
                            'nth': index + 1,
                            'min_val': min_possible_value,
                            'max_val': max_possible_value,
                        },
                        code='effects_value_invalid'
                    )
                })

            if value < min_possible_value or value > max_possible_value:
                raise ValidationError({
                    'effects_value': ValidationError(
                        'Effect %(nth)s: Must be between %(min_val)s and %(max_val)s.',
                        params={
                            'nth': index + 1,
                            'min_val': min_possible_value,
                            'max_val': max_possible_value,
                        },
                        code='effects_value_invalid'
                    )
                })

        # Set derived field values after all cleaning is done
        self._update_values()

    def save(self, *args, **kwargs):
        self._update_values()
        super().save(*args, **kwargs)

    def _update_values(self):
        # Main stat value based on stat/level
        self.main_stat_value = self.MAIN_STAT_VALUES[self.main_stat][self.level]

        # Quality based on number of secondary effects
        self.quality = len([eff for eff in self.effects if eff])

        # Efficiency
        # Compare effect values against a perfectly upgraded legendary artifact with the same effects
        total_roll_rating = sum([
            val / float(self.EFFECT_VALUES[eff]['max'])
            for eff, val in zip(self.effects, self.effects_value)
        ])
        self.efficiency = total_roll_rating / 8 * 100

        # Max Efficiency
        # The maximum potential assuming all future rolls are perfect
        rolls_remaining = 4 - self.effect_upgrades_received
        self.max_efficiency = (total_roll_rating + rolls_remaining) / 8 * 100

    def get_precise_slot_display(self):
        return self.get_archetype_display() or self.get_element_display()

    def get_main_stat_artifact_display(self):
        return f'{self.get_main_stat_display()} +{self.main_stat_value}'

    def get_effects_display(self):
        return [
            self.EFFECT_STRINGS[eff].format(self.effects_value[idx]) for idx, eff in enumerate(self.effects)
        ]

    @property
    def effect_upgrades_received(self):
        return int(floor(min(self.level, 12) / 3))


class ArtifactCraft(ArtifactObjectBase):
    # Quality is only attribute that affects potential value
    # [effect][quality]
    EFFECT_VALUES = {
        ArtifactObjectBase.EFFECT_ATK_LOST_HP: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 9, 'max': 20},
            ArtifactObjectBase.QUALITY_HERO: {'min': 12, 'max': 20},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 14, 'max': 20},
        },
        ArtifactObjectBase.EFFECT_DEF_LOST_HP: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 9, 'max': 20},
            ArtifactObjectBase.QUALITY_HERO: {'min': 12, 'max': 20},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 14, 'max': 20},
        },
        ArtifactObjectBase.EFFECT_SPD_LOST_HP: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 9, 'max': 20},
            ArtifactObjectBase.QUALITY_HERO: {'min': 12, 'max': 20},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 14, 'max': 20},
        },
        ArtifactObjectBase.EFFECT_SPD_INABILITY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_ATK: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
            ArtifactObjectBase.QUALITY_HERO: {'min': 4, 'max': 8},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 8},
        },
        ArtifactObjectBase.EFFECT_DEF: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_SPD: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_CRIT_RATE: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_COUNTER_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_COOP_ATTACK_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_BOMB_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_REFLECT_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 1, 'max': 5},
            ArtifactObjectBase.QUALITY_HERO: {'min': 2, 'max': 5},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 3, 'max': 5},
        },
        ArtifactObjectBase.EFFECT_CRUSHING_HIT_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_DMG_RECEIVED_INABILITY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 1, 'max': 5},
            ArtifactObjectBase.QUALITY_HERO: {'min': 2, 'max': 5},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 3, 'max': 5},
        },
        ArtifactObjectBase.EFFECT_CRIT_DMG_RECEIVED: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_LIFE_DRAIN: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 5, 'max': 12},
            ArtifactObjectBase.QUALITY_HERO: {'min': 7, 'max': 12},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 8, 'max': 12},
        },
        ArtifactObjectBase.EFFECT_HP_REVIVE: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_ATB_REVIVE: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_HP: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 0.2, 'max': 0.5},
            ArtifactObjectBase.QUALITY_HERO: {'min': 0.3, 'max': 0.5},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 0.4, 'max': 0.5},
        },
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_ATK: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_DEF: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_DMG_PCT_OF_SPD: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 25, 'max': 60},
            ArtifactObjectBase.QUALITY_HERO: {'min': 30, 'max': 60},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 40, 'max': 60},
        },
        ArtifactObjectBase.EFFECT_CRIT_DMG_UP_ENEMY_HP_GOOD: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_CRIT_DMG_UP_ENEMY_HP_BAD: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 8, 'max': 18},
            ArtifactObjectBase.QUALITY_HERO: {'min': 10, 'max': 18},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 12, 'max': 18},
        },
        ArtifactObjectBase.EFFECT_CRIT_DMG_SINGLE_TARGET: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 2, 'max': 6},
            ArtifactObjectBase.QUALITY_HERO: {'min': 3, 'max': 6},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 4, 'max': 6},
        },
        ArtifactObjectBase.EFFECT_DMG_TO_FIRE: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
            ArtifactObjectBase.QUALITY_HERO: {'min': 4, 'max': 8},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 8},
        },
        ArtifactObjectBase.EFFECT_DMG_TO_WATER: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
            ArtifactObjectBase.QUALITY_HERO: {'min': 4, 'max': 8},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 8},
        },
        ArtifactObjectBase.EFFECT_DMG_TO_WIND: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
            ArtifactObjectBase.QUALITY_HERO: {'min': 4, 'max': 8},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 8},
        },
        ArtifactObjectBase.EFFECT_DMG_TO_LIGHT: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
            ArtifactObjectBase.QUALITY_HERO: {'min': 4, 'max': 8},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 8},
        },
        ArtifactObjectBase.EFFECT_DMG_TO_DARK: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 3, 'max': 8},
            ArtifactObjectBase.QUALITY_HERO: {'min': 4, 'max': 8},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 5, 'max': 8},
        },
        ArtifactObjectBase.EFFECT_DMG_FROM_FIRE: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_DMG_FROM_WATER: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_DMG_FROM_WIND: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_DMG_FROM_LIGHT: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_DMG_FROM_DARK: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK1_CRIT_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK2_CRIT_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK3_CRIT_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK4_CRIT_DMG: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK1_RECOVERY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK2_RECOVERY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK3_RECOVERY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK1_ACCURACY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK2_ACCURACY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
        ArtifactObjectBase.EFFECT_SK3_ACCURACY: {
            ArtifactObjectBase.QUALITY_RARE: {'min': 4, 'max': 9},
            ArtifactObjectBase.QUALITY_HERO: {'min': 5, 'max': 9},
            ArtifactObjectBase.QUALITY_LEGEND: {'min': 7, 'max': 9},
        },
    }

    effect = models.IntegerField(choices=ArtifactObjectBase.EFFECT_CHOICES)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.get_quality_display()} Artifact Craft - {self.effect_description}'

    @property
    def min_value(self):
        return self.EFFECT_VALUES[self.effect][self.quality]['min']

    @property
    def max_value(self):
        return self.EFFECT_VALUES[self.effect][self.quality]['max']

    @property
    def effect_description(self):
        return self.EFFECT_STRINGS[self.effect].format(f'{self.min_value}-{self.max_value}')
