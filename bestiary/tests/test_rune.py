from django.test import TestCase

from .. import models


class Efficiencies(TestCase):
    def stub_rune(self, level=0, stars=6, main=models.Rune.STAT_HP_PCT, type=models.Rune.TYPE_ENERGY,
                  substats=None, substat_values=None):
        """provide template for arbitrary rune with required fields populated"""
        if substats is None:
            substats = []
        if substat_values is None:
            substat_values = []

        rune = models.Rune(
            stars=stars,
            level=level,
            slot=2,
            main_stat=main,
            main_stat_value=models.Rune.MAIN_STAT_VALUES[main][stars][level],
            substats=substats,
            substat_values=substat_values,
            type=type,
        )
        rune.update_fields()

        return rune

    def test_efficiencies_star_6_level_15(self):
        """Baseline test of max-level rune"""
        rune = self.stub_rune(level=15)

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.get_efficiency(),
        )
        # no upgrades left
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_6_level_12(self):
        """No upgrades are left so this should match the max level test"""
        rune = self.stub_rune(level=12)

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.get_efficiency(),
        )
        # no upgrades left
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_6_level_0(self):
        rune = self.stub_rune(level=0)

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.get_efficiency(),
        )
        # four max upgrades (as 6*, at 100% of 20%)
        self.assertAlmostEqual(
            (1.0 + 4 * 0.2) / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_5_level_0_existing(self):
        rune = self.stub_rune(
            level=0,
            stars=5,
            substats=[
                models.Rune.STAT_HP_PCT,
                models.Rune.STAT_ATK_PCT,
                models.Rune.STAT_DEF_PCT,
                # efficiency is always worse than % of base stats
                models.Rune.STAT_HP,
            ],
            substat_values=[0, 0, 0, 0],
        )

        self.assertAlmostEqual(
            (51 / 63) / 2.8 * 100,
            rune.get_efficiency(),
        )
        # four base% upgrades (as 5*, at 88% of 20%)
        self.assertAlmostEqual(
            (51 / 63 + 4 * 0.875 * 0.2) / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_5_level_0_new_base(self):
        rune = self.stub_rune(level=6, stars=5)

        self.assertAlmostEqual(
            (51 / 63) / 2.8 * 100,
            rune.get_efficiency(),
        )
        # two base % upgrades (as 5*, at 88% of 20%)
        self.assertAlmostEqual(
            (51 / 63 + 2 * 0.875 * 0.2) / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_4_level_0_existing(self):
        rune = self.stub_rune(
            level=0,
            stars=4,
            substats=[
                models.Rune.STAT_HP_PCT,
                models.Rune.STAT_ATK_PCT,
                models.Rune.STAT_DEF_PCT,
                # efficiency is always worse than % of base stats
                models.Rune.STAT_HP,
            ],
            substat_values=[0, 0, 0, 0],
        )

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.get_efficiency(),
        )
        # four base% upgrades (as 4*, at 75% of 20%)
        self.assertAlmostEqual(
            (43 / 63 + 4 * 0.75 * 0.2) / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_4_level_6_new_base(self):
        """Two upgrades left; a 4* should get the (max) base % upgrades"""
        rune = self.stub_rune(level=6, stars=4)

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.get_efficiency(),
        )
        # two base% upgrades (as 4*, at 75% of 20%)
        self.assertAlmostEqual(
            (43 / 63 + 2 * 0.75 * 0.2) / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_4_level_9_new_base(self):
        rune = self.stub_rune(
            level=9,
            stars=4,
            # exclude base% stats to force upgrade to CD
            substats=[
                models.Rune.STAT_HP_PCT,
                models.Rune.STAT_ATK_PCT,
                models.Rune.STAT_DEF_PCT,
            ],
            substat_values=[0, 0, 0],
        )

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.get_efficiency(),
        )
        # base %, ACC, and RES are all on the same scale so we'll always get a 75% this way
        self.assertAlmostEqual(
            (43 / 63 + 1 * 0.75 * 0.2) / 2.8 * 100,
            rune.get_max_efficiency(),
        )

    def test_efficiencies_star_4_level_9_existing_cr(self):
        rune = self.stub_rune(
            level=0,
            stars=4,
            # exclude base% stats to force upgrade to CD
            substats=[
                models.Rune.STAT_CRIT_RATE_PCT,
            ],
            substat_values=[0],
        )

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.get_efficiency(),
        )
        # one at CR and 3x at BASE %
        self.assertAlmostEqual(
            (43 / 63 + 1 * 4/6 * 0.2 + 3 * 0.75 * 0.2) / 2.8 * 100,
            rune.get_max_efficiency(),
        )
