from django.core.exceptions import ValidationError
from django.test import TestCase

from bestiary import models


class Rune(models.Rune):
    # Add an easy to use stub function
    class Meta:
        abstract = True
        
    @classmethod
    def stub(cls, **kwargs):
        defaults = {
            'type': Rune.TYPE_ENERGY,
            'stars': 6,
            'level': 0,
            'slot': 2,
            'main_stat': Rune.STAT_HP_PCT,
            'innate_stat': None,
            'innate_stat_value': None,
            'substats': [],
            'substat_values': [],
            'substats_enchanted': [],
            'substats_grind_value': [],
        }

        defaults.update(kwargs)
        rune = cls(**defaults)
        rune.update_fields()

        return rune


class Stats(TestCase):
    def test_main_stat_value_auto_populated(self):
        rune = Rune.stub()
        self.assertIsNotNone(rune.main_stat_value)
        self.assertGreater(rune.main_stat_value, 0)

    def test_main_stat_value_capped_when_updating(self):
        rune = Rune.stub()
        rune.main_stat_value = 99999
        rune.update_fields()
        self.assertEqual(
            rune.main_stat_value,
            Rune.MAIN_STAT_VALUES[rune.main_stat][rune.stars][rune.level]
        )

    def test_main_stat_value_missing_when_cleaning(self):
        rune = Rune.stub()
        rune.main_stat_value = None
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('main_stat_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['main_stat_value'][0].code, 'main_stat_missing_value')

    def test_main_stat_value_exception_when_cleaning(self):
        rune = Rune.stub()
        rune.main_stat_value = 99999
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('main_stat_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['main_stat_value'][0].code, 'main_stat_value_invalid')

    def test_substat_arrays_always_same_length(self):
        rune = Rune.stub(
            substats=[
                Rune.STAT_HP,
                Rune.STAT_ATK,
                Rune.STAT_CRIT_DMG_PCT,
            ],
            substat_values=[4, 4, 4]
        )
        rune.clean()

        self.assertEqual(len(rune.substats), 3)
        self.assertEqual(len(rune.substat_values), 3)
        self.assertEqual(len(rune.substats_enchanted), 3)
        self.assertEqual(len(rune.substats_grind_value), 3)

    def test_substat_enchanted_defaults_false(self):
        rune = Rune.stub(
            substats=[
                Rune.STAT_HP,
                Rune.STAT_ATK,
                Rune.STAT_CRIT_DMG_PCT,
            ],
            substat_values=[4, 4, 4]
        )
        rune.clean()
        self.assertFalse(any(rune.substats_enchanted))

    def test_substat_grind_value_defaults_zero(self):
        rune = Rune.stub(
            substats=[
                Rune.STAT_HP,
                Rune.STAT_ATK,
                Rune.STAT_CRIT_DMG_PCT,
            ],
            substat_values=[4, 4, 4]
        )
        rune.clean()
        self.assertEqual(sum(rune.substats_grind_value), 0)

    def test_no_substat_upgrades_received(self):
        rune = Rune.stub(level=0)
        self.assertEqual(rune.substat_upgrades_received, 0)
        self.assertEqual(rune.substat_upgrades_remaining, 4)

    def test_one_substat_upgrades_received(self):
        rune = Rune.stub(level=3)
        self.assertEqual(rune.substat_upgrades_received, 1)
        self.assertEqual(rune.substat_upgrades_remaining, 3)

    def test_two_substat_upgrades_received(self):
        rune = Rune.stub(level=6)
        self.assertEqual(rune.substat_upgrades_received, 2)
        self.assertEqual(rune.substat_upgrades_remaining, 2)

    def test_three_substat_upgrades_received(self):
        rune = Rune.stub(level=9)
        self.assertEqual(rune.substat_upgrades_received, 3)
        self.assertEqual(rune.substat_upgrades_remaining, 1)

    def test_all_substat_upgrades_received(self):
        rune = Rune.stub(level=12)
        self.assertEqual(rune.substat_upgrades_received, 4)
        self.assertEqual(rune.substat_upgrades_remaining, 0)

    def test_lv0_required_number_of_substats(self):
        rune = Rune.stub(level=0)

        try:
            rune.clean()
        except ValidationError:
            self.fail()

    def test_lv3_not_enough_substats(self):
        rune = Rune.stub(level=3, substats=[], substat_values=[])
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('substats', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['substats'][0].code, 'not_enough_substats')

    def test_lv3_enough_substats(self):
        rune = Rune.stub(
            level=3,
            substats=[Rune.STAT_HP],
            substat_values=[4],
        )
        try:
            rune.clean()
        except ValidationError:
            self.fail()

    def test_lv6_not_enough_substats(self):
        rune = Rune.stub(
            level=6,
            substats=[Rune.STAT_HP],
            substat_values=[4]
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('substats', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['substats'][0].code, 'not_enough_substats')

    def test_lv6_enough_substats(self):
        rune = Rune.stub(
            level=3,
            substats=[Rune.STAT_HP, Rune.STAT_ACCURACY_PCT],
            substat_values=[4, 4],
        )
        try:
            rune.clean()
        except ValidationError:
            self.fail()

    def test_lv9_not_enough_substats(self):
        rune = Rune.stub(
            level=9,
            substats=[Rune.STAT_HP, Rune.STAT_ACCURACY_PCT],
            substat_values=[4, 4]
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('substats', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['substats'][0].code, 'not_enough_substats')

    def test_lv9_enough_substats(self):
        rune = Rune.stub(
            level=9,
            substats=[Rune.STAT_HP, Rune.STAT_ACCURACY_PCT, Rune.STAT_ATK],
            substat_values=[4, 4, 4],
        )
        try:
            rune.clean()
        except ValidationError:
            self.fail()

    def test_lv12_not_enough_substats(self):
        rune = Rune.stub(
            level=12,
            substats=[Rune.STAT_HP, Rune.STAT_ACCURACY_PCT, Rune.STAT_ATK],
            substat_values=[4, 4, 4]
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('substats', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['substats'][0].code, 'not_enough_substats')

    def test_lv12_enough_substats(self):
        rune = Rune.stub(
            level=12,
            substats=[Rune.STAT_HP, Rune.STAT_ACCURACY_PCT, Rune.STAT_ATK, Rune.STAT_DEF],
            substat_values=[4, 4, 4, 4],
        )
        try:
            rune.clean()
        except ValidationError:
            self.fail()


class Efficiency(TestCase):
    def test_efficiencies_star_6_level_15(self):
        """Baseline test of max-level rune"""
        rune = Rune.stub(level=15)

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.efficiency,
        )
        # no upgrades left
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_6_level_12(self):
        """No upgrades are left so this should match the max level test"""
        rune = Rune.stub(level=12)

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.efficiency,
        )
        # no upgrades left
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_6_level_0(self):
        rune = Rune.stub(level=0)

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.efficiency,
        )
        # four max upgrades (as 6*, at 100% of 20%)
        self.assertAlmostEqual(
            (1.0 + 4 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_5_level_0_existing(self):
        rune = Rune.stub(
            level=0,
            stars=5,
            substats=[
                Rune.STAT_HP_PCT,
                Rune.STAT_ATK_PCT,
                Rune.STAT_DEF_PCT,
                # efficiency is always worse than % of base stats
                Rune.STAT_HP,
            ],
            substat_values=[0, 0, 0, 0],
        )

        self.assertAlmostEqual(
            (51 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # four base% upgrades (as 5*, at 88% of 20%)
        self.assertAlmostEqual(
            (51 / 63 + 4 * 0.875 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_5_level_0_new_base(self):
        rune = Rune.stub(level=6, stars=5)

        self.assertAlmostEqual(
            (51 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # two base % upgrades (as 5*, at 88% of 20%)
        self.assertAlmostEqual(
            (51 / 63 + 2 * 0.875 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_4_level_0_existing(self):
        rune = Rune.stub(
            level=0,
            stars=4,
            substats=[
                Rune.STAT_HP_PCT,
                Rune.STAT_ATK_PCT,
                Rune.STAT_DEF_PCT,
                # efficiency is always worse than % of base stats
                Rune.STAT_HP,
            ],
            substat_values=[0, 0, 0, 0],
        )

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # four base% upgrades (as 4*, at 75% of 20%)
        self.assertAlmostEqual(
            (43 / 63 + 4 * 0.75 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_4_level_6_new_base(self):
        """Two upgrades left; a 4* should get the (max) base % upgrades"""
        rune = Rune.stub(level=6, stars=4)

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # two base% upgrades (as 4*, at 75% of 20%)
        self.assertAlmostEqual(
            (43 / 63 + 2 * 0.75 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_4_level_9_new_base(self):
        rune = Rune.stub(
            level=9,
            stars=4,
            # exclude base% stats to force upgrade to CD
            substats=[
                Rune.STAT_HP_PCT,
                Rune.STAT_ATK_PCT,
                Rune.STAT_DEF_PCT,
            ],
            substat_values=[0, 0, 0],
        )

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # base %, ACC, and RES are all on the same scale so we'll always get a 75% this way
        self.assertAlmostEqual(
            (43 / 63 + 1 * 0.75 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )

    def test_efficiencies_star_4_level_9_existing_cr(self):
        rune = Rune.stub(
            level=0,
            stars=4,
            # exclude base% stats to force upgrade to CD
            substats=[
                Rune.STAT_CRIT_RATE_PCT,
            ],
            substat_values=[0],
        )

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # one at CR and 3x at BASE %
        self.assertAlmostEqual(
            (43 / 63 + 1 * 4/6 * 0.2 + 3 * 0.75 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )
