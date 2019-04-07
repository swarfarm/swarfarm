from django.contrib.auth.models import User
from django.test import TestCase

from herders.models import Summoner
from .. import models


class Efficiencies(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username='test')
        self.summoner = Summoner.objects.create(user=self.user)

    def stub_rune(self, level=0, stars=6, main=models.RuneInstance.STAT_HP_PCT, type=models.RuneInstance.TYPE_ENERGY,
                  substats=None, substat_values=None):
        """provide template for arbitrary rune with required fields populated"""
        rune = models.RuneInstance(
            owner=self.summoner,
            stars=stars,
            level=level,
            slot=2,
            main_stat=main,
            main_stat_value=models.RuneInstance.MAIN_STAT_VALUES[main][stars][level],
            substats=[],
            substat_values=[],
            type=type,
        )

        if substats is not None:
            for i, stat in enumerate(substats):
                setattr(rune, 'substat_{}'.format(i+1), stat)
                setattr(rune, 'substat_{}_value'.format(i+1), substat_values[i])

        return rune

    def test_efficiencies_star_6_level_15(self):
        """Baseline test of max-level rune"""
        rune = self.stub_rune(level=15)
        rune.save()

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.efficiency,
        )
        # no upgrades left
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.max_efficiency,
        )
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.get_avg_efficiency(rune.efficiency, rune.substat_upgrades_remaining),
        )

    def test_efficiencies_star_6_level_12(self):
        """No upgrades are left so this should match the max level test"""
        rune = self.stub_rune(level=12)
        rune.save()

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.efficiency,
        )
        # no upgrades left
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.max_efficiency,
        )
        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.get_avg_efficiency(rune.efficiency, rune.substat_upgrades_remaining),
        )

    def test_efficiencies_star_6_level_0(self):
        rune = self.stub_rune(level=0)
        rune.save()

        self.assertAlmostEqual(
            1.0 / 2.8 * 100,
            rune.efficiency,
        )
        # four max upgrades (as 6*, at 100% of 20%)
        self.assertAlmostEqual(
            (1.0 + 4 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )
        upgrades_level_6 = [v[6] for stat, v in rune.UPGRADE_VALUES_AVG.items() if stat != rune.main_stat]
        self.assertAlmostEqual(
            (1.0 + 4 * 0.2 * sum(upgrades_level_6) / len(upgrades_level_6)) / 2.8 * 100,
            rune.get_avg_efficiency(rune.efficiency, rune.substat_upgrades_remaining),
        )

    def test_efficiencies_star_5_level_0_existing(self):
        rune = self.stub_rune(
            level=0,
            stars=5,
            substats=[
                models.RuneInstance.STAT_HP_PCT,
                models.RuneInstance.STAT_ATK_PCT,
                models.RuneInstance.STAT_DEF_PCT,
                # efficiency is always worse than % of base stats
                models.RuneInstance.STAT_HP,
            ],
            substat_values=[0, 0, 0, 0],
        )
        rune.save()

        self.assertAlmostEqual(
            (51 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # four base% upgrades (as 5*, at 88% of 20%)
        self.assertAlmostEqual(
            (51 / 63 + 4 * 0.875 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )
        # four upgrades to existing runes
        upgrades = [rune.UPGRADE_VALUES_AVG[rune.STAT_HP_PCT][5], rune.UPGRADE_VALUES_AVG[rune.STAT_ATK_PCT][5],
                    rune.UPGRADE_VALUES_AVG[rune.STAT_DEF_PCT][5], rune.UPGRADE_VALUES_AVG[rune.STAT_HP][5]]
        self.assertAlmostEqual(
            (51 / 63 + 4 * 0.2 * sum(upgrades) / len(upgrades)) / 2.8 * 100,
            rune.get_avg_efficiency(rune.efficiency, rune.substat_upgrades_remaining),
        )

    def test_efficiencies_star_5_level_6_new_base(self):
        rune = self.stub_rune(level=6, stars=5)
        rune.save()

        self.assertAlmostEqual(
            (51 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # two base % upgrades (as 5*, at 88% of 20%)
        self.assertAlmostEqual(
            (51 / 63 + 2 * 0.875 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )
        upgrades_level_5 = [v[5] for stat, v in rune.UPGRADE_VALUES_AVG.items() if stat != rune.main_stat]
        self.assertAlmostEqual(
            (51 / 63 + 2 * 0.2 * sum(upgrades_level_5) / len(upgrades_level_5)) / 2.8 * 100,
            rune.get_avg_efficiency(rune.efficiency, rune.substat_upgrades_remaining),
        )

    def test_efficiencies_star_4_level_0_existing(self):
        rune = self.stub_rune(
            level=0,
            stars=4,
            substats=[
                models.RuneInstance.STAT_HP_PCT,
                models.RuneInstance.STAT_ATK_PCT,
                models.RuneInstance.STAT_DEF_PCT,
                # efficiency is always worse than % of base stats
                models.RuneInstance.STAT_HP,
            ],
            substat_values=[0, 0, 0, 0],
        )
        rune.save()

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # four base% upgrades (as 4*, at 75% of 20%)
        self.assertAlmostEqual(
            (43 / 63 + 4 * 0.75 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )
        # four upgrades to existing runes
        upgrades = [rune.UPGRADE_VALUES_AVG[rune.STAT_HP_PCT][4], rune.UPGRADE_VALUES_AVG[rune.STAT_ATK_PCT][4],
                    rune.UPGRADE_VALUES_AVG[rune.STAT_DEF_PCT][4], rune.UPGRADE_VALUES_AVG[rune.STAT_HP][4]]
        self.assertAlmostEqual(
            (43 / 63 + 4 * 0.2 * sum(upgrades) / len(upgrades)) / 2.8 * 100,
            rune.get_avg_efficiency(rune.efficiency, rune.substat_upgrades_remaining),
        )

    def test_efficiencies_star_4_level_6_new_base(self):
        """Two upgrades left; a 4* should get the (max) base % upgrades"""
        rune = self.stub_rune(level=6, stars=4)
        rune.save()

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # two base% upgrades (as 4*, at 75% of 20%)
        self.assertAlmostEqual(
            (43 / 63 + 2 * 0.75 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )
        # two average upgrades
        upgrades_level_4 = [v[4] for stat, v in rune.UPGRADE_VALUES_AVG.items() if stat != rune.main_stat]
        self.assertAlmostEqual(
            (43 / 63 + 2 * 0.2 * sum(upgrades_level_4) / len(upgrades_level_4)) / 2.8 * 100,
            rune.get_avg_efficiency(rune.efficiency, rune.substat_upgrades_remaining),
        )

    def test_efficiencies_star_4_level_9_new_base(self):
        rune = self.stub_rune(
            level=9,
            stars=4,
            # exclude base% stats to force upgrade to CD
            substats=[
                models.RuneInstance.STAT_HP_PCT,
                models.RuneInstance.STAT_ATK_PCT,
                models.RuneInstance.STAT_DEF_PCT,
            ],
            substat_values=[0, 0, 0],
        )
        rune.save()

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
        rune = self.stub_rune(
            level=0,
            stars=4,
            # exclude base% stats to force upgrade to CD
            substats=[
                models.RuneInstance.STAT_CRIT_RATE_PCT,
            ],
            substat_values=[0],
        )
        rune.save()

        self.assertAlmostEqual(
            (43 / 63) / 2.8 * 100,
            rune.efficiency,
        )
        # one at CR and 3x at BASE %
        self.assertAlmostEqual(
            (43 / 63 + 1 * 4/6 * 0.2 + 3 * 0.75 * 0.2) / 2.8 * 100,
            rune.max_efficiency,
        )
