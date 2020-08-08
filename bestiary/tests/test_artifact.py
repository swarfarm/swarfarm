from django.core.exceptions import ValidationError
from django.test import TestCase

from bestiary import models


class Artifact(models.Artifact):
    class Meta:
        abstract = True

    @classmethod
    def stub(cls, **kwargs):
        defaults = {
            'slot': models.Artifact.SLOT_ELEMENTAL,
            'element': models.Artifact.ELEMENT_WATER,
            'archetype': None,
            'quality': models.Artifact.QUALITY_NORMAL,
            'original_quality': models.Artifact.QUALITY_NORMAL,
            'level': 0,
            'main_stat': models.Artifact.STAT_HP,
            'effects': [],
            'effects_value': [],
            'effects_upgrade_count': [],
            'effects_reroll_count': [],
        }

        defaults.update(kwargs)
        artifact = cls(**defaults)

        return artifact

    def force_valid_effect_values(self):
        # Update effects values to match selected effects and upgrades received.
        self.effects_value = [self.EFFECT_VALUES[eff]['max'] for eff in self.effects]

        # Upgrades are always applied to first effect
        self.effects_value[0] += self.EFFECT_VALUES[self.effects[0]]['max'] * self.effect_upgrades_received


class Attributes(TestCase):
    def test_level_too_low(self):
        artifact = Artifact.stub(level=-1)
        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()
        self.assertIn('level', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['level'][0].code, 'min_value')

    def test_level_too_high(self):
        artifact = Artifact.stub(level=16)
        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()
        self.assertIn('level', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['level'][0].code, 'max_value')

    def test_quality_normal(self):
        artifact = Artifact.stub(effects=[])
        artifact.full_clean()
        self.assertEqual(artifact.quality, artifact.QUALITY_NORMAL)

    def test_quality_magic(self):
        artifact = Artifact.stub(effects=[Artifact.EFFECT_ATK])
        artifact.force_valid_effect_values()
        artifact.full_clean()
        self.assertEqual(artifact.quality, artifact.QUALITY_MAGIC)

    def test_quality_rare(self):
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_DEF
            ]
        )
        artifact.force_valid_effect_values()
        artifact.full_clean()
        self.assertEqual(artifact.quality, artifact.QUALITY_RARE)

    def test_quality_hero(self):
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_SPD,
            ]
        )
        artifact.force_valid_effect_values()
        artifact.full_clean()
        self.assertEqual(artifact.quality, artifact.QUALITY_HERO)

    def test_quality_legend(self):
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_SPD,
                Artifact.EFFECT_BOMB_DMG,
            ]
        )
        artifact.force_valid_effect_values()
        artifact.full_clean()
        self.assertEqual(artifact.quality, artifact.QUALITY_LEGEND)


class Efficiency(TestCase):
    def test_efficiency_normal_level_0(self):
        """Zero effects = 0% efficiency"""
        artifact = Artifact.stub()
        artifact.full_clean()
        self.assertAlmostEqual(0, artifact.efficiency)

    def test_max_efficiency_normal_level_0(self):
        """No initial rolls, 4 possible rolls on upgrade = 4/8 rolls or 50% max eff"""
        artifact = Artifact.stub()
        artifact.full_clean()
        self.assertAlmostEqual(50, artifact.max_efficiency)

    def test_efficiency_perfect_legend_level_0(self):
        """Received half of possible rolls perfectly so 50% """
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_SPD,
                Artifact.EFFECT_BOMB_DMG,
            ],
            effects_value=[
                Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_DEF]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_SPD]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_BOMB_DMG]['max'],
            ]
        )
        artifact.full_clean()
        self.assertAlmostEqual(50, artifact.efficiency)

    def test_max_efficiency_perfect_legend_level_0(self):
        """Perfect initial rolls, legendary at drop, but no upgrades received"""
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_SPD,
                Artifact.EFFECT_BOMB_DMG,
            ],
            effects_value=[
                Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_DEF]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_SPD]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_BOMB_DMG]['max'],
            ]
        )
        artifact.full_clean()
        self.assertAlmostEqual(100, artifact.max_efficiency)

    def test_efficiency_perfect_legend_lv15(self):
        artifact = Artifact.stub(
            level=15,
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_SPD,
                Artifact.EFFECT_BOMB_DMG,
            ],
            effects_value=[
                Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max'] * 5,  # All upgrades into this eff
                Artifact.EFFECT_VALUES[Artifact.EFFECT_DEF]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_SPD]['max'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_BOMB_DMG]['max'],
            ]
        )
        artifact.full_clean()
        self.assertAlmostEqual(100, artifact.efficiency)
        self.assertAlmostEqual(100, artifact.max_efficiency)

    def test_efficiency_middling_lv15(self):
        atk_upgrades = (Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['min'] +
                        Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max']) / 2
        def_upgrades = (Artifact.EFFECT_VALUES[Artifact.EFFECT_DEF]['min'] +
                        Artifact.EFFECT_VALUES[Artifact.EFFECT_DEF]['max']) / 2
        crushing_upgrades = (Artifact.EFFECT_VALUES[Artifact.EFFECT_CRUSHING_HIT_DMG]['min'] +
                             Artifact.EFFECT_VALUES[Artifact.EFFECT_CRUSHING_HIT_DMG]['max']) / 2
        pct_atk_upgrades = (Artifact.EFFECT_VALUES[Artifact.EFFECT_DMG_PCT_OF_ATK]['min'] +
                            Artifact.EFFECT_VALUES[Artifact.EFFECT_DMG_PCT_OF_ATK]['max']) / 2

        artifact = Artifact.stub(
            level=15,
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_CRUSHING_HIT_DMG,
                Artifact.EFFECT_DMG_PCT_OF_ATK,
            ],
            effects_value=[
                atk_upgrades * 5,  # All upgrades into this effect
                def_upgrades,
                crushing_upgrades,
                pct_atk_upgrades,
            ]
        )
        artifact.full_clean()
        self.assertAlmostEqual(75, artifact.efficiency)
        self.assertAlmostEqual(75, artifact.max_efficiency)


class Stats(TestCase):
    def test_value_set_automatically_lv0(self):
        artifact = Artifact.stub(
            level=0,
            main_stat=Artifact.STAT_HP,
        )
        artifact.full_clean()
        self.assertEqual(artifact.main_stat_value, Artifact.MAIN_STAT_VALUES[Artifact.STAT_HP][0])

    def test_value_set_automatically_lv3(self):
        artifact = Artifact.stub(
            level=3,
            main_stat=Artifact.STAT_HP,
            effects=[Artifact.EFFECT_ATK],
            effects_value=[
                Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['min']
            ]
        )
        artifact.full_clean()
        self.assertEqual(artifact.main_stat_value, Artifact.MAIN_STAT_VALUES[Artifact.STAT_HP][3])

    def test_value_set_automatically_lv15(self):
        artifact = Artifact.stub(
            level=15,
            main_stat=Artifact.STAT_HP,
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_BOMB_DMG,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_SPD,
            ],
            effects_value=[
                Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['min'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_BOMB_DMG]['min'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_DEF]['min'],
                Artifact.EFFECT_VALUES[Artifact.EFFECT_SPD]['min'],
            ]
        )
        artifact.full_clean()
        self.assertEqual(artifact.main_stat_value, Artifact.MAIN_STAT_VALUES[Artifact.STAT_HP][15])


class Effects(TestCase):
    def test_unique_effects(self):
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_ATK,
            ]
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects'][0].code, 'effects_duplicate')

    def test_min_number_of_effects_lv12(self):
        artifact = Artifact.stub(
            level=12,
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_SPD,
                Artifact.EFFECT_DEF,
            ]
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects'][0].code, 'effects_not_enough')

    def test_min_number_of_effects_lv9(self):
        artifact = Artifact.stub(
            level=9,
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_SPD,
            ]
        )
        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects'][0].code, 'effects_not_enough')

    def test_min_number_of_effects_lv6(self):
        artifact = Artifact.stub(
            level=6,
            effects=[Artifact.EFFECT_ATK]
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects'][0].code, 'effects_not_enough')

    def test_min_number_of_effects_lv3(self):
        artifact = Artifact.stub(
            level=3,
            effects=[],
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects'][0].code, 'effects_not_enough')

    def test_max_number_of_effects(self):
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_ATK,
                Artifact.EFFECT_SPD,
                Artifact.EFFECT_DEF,
                Artifact.EFFECT_BOMB_DMG,
                Artifact.EFFECT_ATB_REVIVE,
            ]
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects'][0].code, 'max_length')

    def test_too_many_values_truncated(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[
                Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max'],
                5,
            ]

        )
        artifact.full_clean()
        self.assertEqual(len(artifact.effects_value), len(artifact.effects))

    def test_missing_effect_values(self):
        artifact = Artifact.stub(
            effects=[
                Artifact.EFFECT_SPD,
            ],
            effects_value=[]
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects_value'][0].code, 'effects_value_invalid')

    def test_effect_value_too_small(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[1],
            effects_upgrade_count=[0],
            effects_reroll_count=[0],
            level=3,
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects_value'][0].code, 'effects_value_invalid')

    def test_effect_value_too_big(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[99],
            effects_upgrade_count=[0],
            effects_reroll_count=[0],
            level=3,
        )

        with self.assertRaises(ValidationError) as cm:
            artifact.full_clean()

        self.assertIn('effects_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['effects_value'][0].code, 'effects_value_invalid')

    def test_effect_value_just_right(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[8],
            effects_upgrade_count=[0],
            effects_reroll_count=[0],
            level=3,
        )
        # Should not raise any exception
        artifact.full_clean()
        self.assertEqual(artifact.effects_value[0], artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max'] * 2)

    def test_too_many_upgrade_count_truncated(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max']],
            effects_upgrade_count=[1, 2, 3],
        )
        artifact.full_clean()
        self.assertEqual(len(artifact.effects_upgrade_count), len(artifact.effects))

    def test_not_enough_upgrade_count_padded(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max']],
            effects_upgrade_count=[],
            effects_reroll_count=[0],
        )
        artifact.full_clean()
        self.assertEqual(len(artifact.effects_upgrade_count), len(artifact.effects))
        self.assertEqual(artifact.effects_upgrade_count[0], 0)

    def test_too_many_reroll_count_truncated(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max']],
            effects_upgrade_count=[0],
            effects_reroll_count=[1, 2, 3],
        )
        artifact.full_clean()
        self.assertEqual(len(artifact.effects_reroll_count), len(artifact.effects))

    def test_not_enough_reroll_count_padded(self):
        artifact = Artifact.stub(
            effects=[Artifact.EFFECT_ATK],
            effects_value=[Artifact.EFFECT_VALUES[Artifact.EFFECT_ATK]['max']],
            effects_upgrade_count=[0],
            effects_reroll_count=[],
        )
        artifact.full_clean()
        self.assertEqual(len(artifact.effects_reroll_count), len(artifact.effects))
        self.assertEqual(artifact.effects_reroll_count[0], 0)

