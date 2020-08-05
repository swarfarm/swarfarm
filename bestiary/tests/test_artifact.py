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
        self.effects_value[0] += self.EFFECT_VALUES[self.effects[0]]['max'] * self.substat_upgrades_received


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


class Stats(TestCase):
    # TODO: Main stat testing
    pass


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
