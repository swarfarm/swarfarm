from django.core.exceptions import ValidationError
from django.test import TestCase

from bestiary import models


class Rune(models.Rune):
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


class Attributes(TestCase):
    def test_stars_too_high_when_cleaning(self):
        rune = Rune.stub()
        rune.stars = 9
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('stars', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['stars'][0].code, 'stars_invalid')

    def test_stars_too_low_when_cleaning(self):
        rune = Rune.stub()
        rune.stars = 0
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('stars', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['stars'][0].code, 'stars_invalid')

    def test_stars_missing_when_cleaning(self):
        rune = Rune.stub()
        rune.stars = None
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('stars', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['stars'][0].code, 'stars_missing')

    def test_level_too_high_when_cleaning(self):
        rune = Rune.stub()
        rune.level = 20
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('level', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['level'][0].code, 'level_invalid')

    def test_level_too_low_when_cleaning(self):
        rune = Rune.stub()
        rune.level = -1
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('level', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['level'][0].code, 'level_invalid')

    def test_level_missing_when_cleaning(self):
        rune = Rune.stub()
        rune.level = None
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('level', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['level'][0].code, 'level_missing')

    def test_slot_too_high_when_cleaning(self):
        rune = Rune.stub()
        rune.slot = 9
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('slot', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['slot'][0].code, 'slot_invalid')

    def test_slot_too_low_when_cleaning(self):
        rune = Rune.stub()
        rune.slot = 0
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('slot', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['slot'][0].code, 'slot_invalid')

    def test_slot_missing_when_cleaning(self):
        rune = Rune.stub()
        rune.slot = None
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('slot', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['slot'][0].code, 'slot_missing')

    def test_level_too_low_when_enchant_applied(self):
        rune = Rune.stub(
            level=11,
            substats=[Rune.STAT_RESIST_PCT, Rune.STAT_ACCURACY_PCT, Rune.STAT_HP, Rune.STAT_ATK],
            substat_values=[4, 4, 4, 4],
            substats_enchanted=[True, False, False, False],
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('level', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['level'][0].code, 'level_invalid')

    def test_quality_normal(self):
        rune = Rune.stub()
        self.assertEqual(rune.quality, Rune.QUALITY_NORMAL)

    def test_quality_magic(self):
        rune = Rune.stub(
            substats=[Rune.STAT_ATK],
            substat_values=[4]
        )
        self.assertEqual(rune.quality, Rune.QUALITY_MAGIC)

    def test_quality_rare(self):
        rune = Rune.stub(
            substats=[Rune.STAT_ATK, Rune.STAT_DEF],
            substat_values=[4, 4, 4]
        )
        self.assertEqual(rune.quality, Rune.QUALITY_RARE)

    def test_quality_hero(self):
        rune = Rune.stub(
            substats=[Rune.STAT_ATK, Rune.STAT_DEF, Rune.STAT_ATK_PCT],
            substat_values=[4, 4, 4]
        )
        self.assertEqual(rune.quality, Rune.QUALITY_HERO)

    def test_quality_legend(self):
        rune = Rune.stub(
            substats=[Rune.STAT_ATK, Rune.STAT_DEF, Rune.STAT_ATK_PCT, Rune.STAT_DEF_PCT],
            substat_values=[4, 4, 4, 4]
        )
        self.assertEqual(rune.quality, Rune.QUALITY_LEGEND)

    def test_one_enchant_gem_applied(self):
        rune = Rune.stub(
            level=12,
            substats=[Rune.STAT_ATK, Rune.STAT_DEF, Rune.STAT_ATK_PCT, Rune.STAT_DEF_PCT],
            substat_values=[4, 4, 4, 4],
            substats_enchanted=[True, False, False, False],
        )
        try:
            rune.clean()
        except ValidationError:
            self.fail()

    def test_too_many_enchant_gems_applied(self):
        rune = Rune.stub(
            level=12,
            substats=[Rune.STAT_ATK, Rune.STAT_DEF, Rune.STAT_ATK_PCT, Rune.STAT_DEF_PCT],
            substat_values=[4, 4, 4, 4],
            substats_enchanted=[True, True, False, False],
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('substats_enchanted', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['substats_enchanted'][0].code, 'too_many_enchants')

    def test_does_not_have_enchant_gem_applied(self):
        rune = Rune.stub()
        self.assertFalse(rune.has_gem)

    def test_does_have_enchant_gem_applied(self):
        rune = Rune.stub(
            level=12,
            substats=[Rune.STAT_ATK, Rune.STAT_DEF, Rune.STAT_ATK_PCT, Rune.STAT_DEF_PCT],
            substat_values=[4, 4, 4, 4],
            substats_enchanted=[True, False, False, False],
        )
        self.assertTrue(rune.has_gem)

    def test_does_not_have_grind_applied(self):
        rune = Rune.stub()
        self.assertFalse(rune.has_grind)

    def test_does_have_grind_applied(self):
        rune = Rune.stub(
            level=12,
            substats=[Rune.STAT_ATK, Rune.STAT_DEF, Rune.STAT_ATK_PCT, Rune.STAT_DEF_PCT],
            substat_values=[4, 4, 4, 4],
            substats_grind_value=[4, 0, 0, 0],
        )
        self.assertTrue(rune.has_grind)


class Stats(TestCase):
    def test_duplicate_stats_main_and_innate(self):
        rune = Rune.stub(
            main_stat=Rune.STAT_HP_PCT,
            innate_stat=Rune.STAT_HP_PCT,
            innate_stat_value=8,
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertEqual(cm.exception.code, 'duplicate_stats')

    def test_duplicate_stats_main_and_sub(self):
        rune = Rune.stub(
            main_stat=Rune.STAT_HP_PCT,
            substats=[Rune.STAT_HP_PCT],
            substat_values=[8],
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertEqual(cm.exception.code, 'duplicate_stats')

    def test_duplicate_stats_innate_and_sub(self):
        rune = Rune.stub(
            main_stat=Rune.STAT_ATK_PCT,
            innate_stat=Rune.STAT_HP_PCT,
            innate_stat_value=8,
            substats=[Rune.STAT_HP_PCT],
            substat_values=[8],
        )
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertEqual(cm.exception.code, 'duplicate_stats')

    def test_main_stat_value_auto_populated(self):
        rune = Rune.stub()
        self.assertIsNotNone(rune.main_stat_value)
        self.assertGreater(rune.main_stat_value, 0)

    def test_main_stat_value_capped(self):
        rune = Rune.stub(
            main_stat_value=99999,
        )
        self.assertEqual(
            rune.main_stat_value,
            Rune.MAIN_STAT_VALUES[rune.main_stat][rune.stars][rune.level]
        )

    def test_main_stat_value_missing_when_cleaning(self):
        rune = Rune.stub()
        rune.main_stat_value = None  # rune.update_fields() sets main stat value, so reset it here
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('main_stat_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['main_stat_value'][0].code, 'main_stat_missing')

    def test_main_stat_value_exception_when_cleaning(self):
        rune = Rune.stub()
        rune.main_stat_value = 99999  # rune.update_fields() sets main stat value, so reset it here
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('main_stat_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['main_stat_value'][0].code, 'main_stat_too_high')

    def test_main_stat_slot_1_invalid_stat(self):
        for invalid_stat in [
            Rune.STAT_HP,
            Rune.STAT_HP_PCT,
            Rune.STAT_ATK_PCT,
            Rune.STAT_DEF,
            Rune.STAT_DEF_PCT,
            Rune.STAT_SPD,
            Rune.STAT_CRIT_RATE_PCT,
            Rune.STAT_CRIT_DMG_PCT,
            Rune.STAT_RESIST_PCT,
            Rune.STAT_ACCURACY_PCT,
        ]:
            rune = Rune.stub(slot=1, main_stat=invalid_stat)
            with self.assertRaises(ValidationError) as cm:
                rune.clean()
            self.assertIn('main_stat', cm.exception.error_dict)
            self.assertEqual(cm.exception.error_dict['main_stat'][0].code, 'invalid_main_stat_for_slot')

    def test_main_stat_slot_2_invalid_stat(self):
        for invalid_stat in [
            Rune.STAT_CRIT_RATE_PCT,
            Rune.STAT_CRIT_DMG_PCT,
            Rune.STAT_RESIST_PCT,
            Rune.STAT_ACCURACY_PCT,
        ]:
            rune = Rune.stub(slot=2, main_stat=invalid_stat)
            with self.assertRaises(ValidationError) as cm:
                rune.clean()
            self.assertIn('main_stat', cm.exception.error_dict)
            self.assertEqual(cm.exception.error_dict['main_stat'][0].code, 'invalid_main_stat_for_slot')

    def test_main_stat_slot_3_invalid_stat(self):
        for invalid_stat in [
            Rune.STAT_HP,
            Rune.STAT_HP_PCT,
            Rune.STAT_ATK,
            Rune.STAT_ATK_PCT,
            Rune.STAT_DEF_PCT,
            Rune.STAT_SPD,
            Rune.STAT_CRIT_RATE_PCT,
            Rune.STAT_CRIT_DMG_PCT,
            Rune.STAT_RESIST_PCT,
            Rune.STAT_ACCURACY_PCT,
        ]:
            rune = Rune.stub(slot=3, main_stat=invalid_stat)
            with self.assertRaises(ValidationError) as cm:
                rune.clean()
            self.assertIn('main_stat', cm.exception.error_dict)
            self.assertEqual(cm.exception.error_dict['main_stat'][0].code, 'invalid_main_stat_for_slot')

    def test_main_stat_slot_4_invalid_stat(self):
        for invalid_stat in [
            Rune.STAT_SPD,
            Rune.STAT_RESIST_PCT,
            Rune.STAT_ACCURACY_PCT,
        ]:
            rune = Rune.stub(slot=4, main_stat=invalid_stat)
            with self.assertRaises(ValidationError) as cm:
                rune.clean()
            self.assertIn('main_stat', cm.exception.error_dict)
            self.assertEqual(cm.exception.error_dict['main_stat'][0].code, 'invalid_main_stat_for_slot')

    def test_main_stat_slot_5_invalid_stat(self):
        for invalid_stat in [
            Rune.STAT_HP_PCT,
            Rune.STAT_ATK,
            Rune.STAT_ATK_PCT,
            Rune.STAT_DEF,
            Rune.STAT_DEF_PCT,
            Rune.STAT_SPD,
            Rune.STAT_CRIT_RATE_PCT,
            Rune.STAT_CRIT_DMG_PCT,
            Rune.STAT_RESIST_PCT,
            Rune.STAT_ACCURACY_PCT,
        ]:
            rune = Rune.stub(slot=5, main_stat=invalid_stat)
            with self.assertRaises(ValidationError) as cm:
                rune.clean()
            self.assertIn('main_stat', cm.exception.error_dict)
            self.assertEqual(cm.exception.error_dict['main_stat'][0].code, 'invalid_main_stat_for_slot')

    def test_main_stat_slot_6_invalid_stat(self):
        for invalid_stat in [
            Rune.STAT_SPD,
            Rune.STAT_CRIT_RATE_PCT,
            Rune.STAT_CRIT_DMG_PCT,
        ]:
            rune = Rune.stub(slot=6, main_stat=invalid_stat)
            with self.assertRaises(ValidationError) as cm:
                rune.clean()
            self.assertIn('main_stat', cm.exception.error_dict)
            self.assertEqual(cm.exception.error_dict['main_stat'][0].code, 'invalid_main_stat_for_slot')

    def test_innate_stat_specified_but_value_missing_when_cleaning(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_HP,
            innate_stat_value=0,
        )
        rune.innate_stat_value = None

        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('innate_stat_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['innate_stat_value'][0].code, 'innate_stat_missing')

    def test_innate_stat_value_capped(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_HP,
            innate_stat_value=99999,
        )
        self.assertEqual(rune.innate_stat_value, Rune.SUBSTAT_INCREMENTS[Rune.STAT_HP][rune.stars])

    def test_innate_stat_value_too_large_when_cleaning(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_HP,
            innate_stat_value=0,
        )
        rune.innate_stat_value = 999  # rune.update_fields() caps it, so reset it here

        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('innate_stat_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['innate_stat_value'][0].code, 'innate_stat_too_high')

    def test_innate_stat_value_too_small_when_cleaning(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_HP,
            innate_stat_value=0,
        )

        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('innate_stat_value', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['innate_stat_value'][0].code, 'innate_stat_too_low')

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

    def test_substat_values_limited_no_upgrades_received(self):
        rune = Rune.stub(
            level=0,
            stars=6,
            substats=[Rune.STAT_ATK_PCT],
            substat_values=[999]
        )
        self.assertEqual(rune.substat_values[0], Rune.SUBSTAT_INCREMENTS[Rune.STAT_ATK_PCT][rune.stars])

    def test_substat_values_limited_all_upgrades_received(self):
        rune = Rune.stub(
            level=12,
            stars=6,
            substats=[Rune.STAT_ATK_PCT, Rune.STAT_ATK, Rune.STAT_DEF, Rune.STAT_DEF_PCT],
            substat_values=[999, 4, 4, 4]
        )
        self.assertEqual(rune.substat_values[0], Rune.SUBSTAT_INCREMENTS[Rune.STAT_ATK_PCT][rune.stars] * 5)

    def test_substat_value_limit_when_cleaning(self):
        rune = Rune.stub(
            level=0,
            stars=6,
            substats=[Rune.STAT_ATK_PCT],
            substat_values=[0],
        )
        rune.substat_values[0] = 999
        with self.assertRaises(ValidationError) as cm:
            rune.clean()
        self.assertIn('substat_values', cm.exception.error_dict)
        self.assertEqual(cm.exception.error_dict['substat_values'][0].code, 'substat_too_high')

    def test_has_hp_flat(self):
        rune = Rune.stub(substats=[Rune.STAT_HP], substat_values=[0])
        self.assertTrue(rune.has_hp)

    def test_has_hp_pct(self):
        rune = Rune.stub(substats=[Rune.STAT_HP_PCT], substat_values=[0])
        self.assertTrue(rune.has_hp)

    def test_has_atk_flat(self):
        rune = Rune.stub(substats=[Rune.STAT_ATK], substat_values=[0])
        self.assertTrue(rune.has_atk)

    def test_has_atk_pct(self):
        rune = Rune.stub(substats=[Rune.STAT_ATK_PCT], substat_values=[0])
        self.assertTrue(rune.has_atk)

    def test_has_def_flat(self):
        rune = Rune.stub(substats=[Rune.STAT_DEF], substat_values=[0])
        self.assertTrue(rune.has_def)

    def test_has_def_pct(self):
        rune = Rune.stub(substats=[Rune.STAT_DEF_PCT], substat_values=[0])
        self.assertTrue(rune.has_def)

    def test_has_crit_rate(self):
        rune = Rune.stub(substats=[Rune.STAT_CRIT_RATE_PCT], substat_values=[0])
        self.assertTrue(rune.has_crit_rate)

    def test_has_crit_dmg(self):
        rune = Rune.stub(substats=[Rune.STAT_CRIT_DMG_PCT], substat_values=[0])
        self.assertTrue(rune.has_crit_dmg)

    def test_has_speed(self):
        rune = Rune.stub(substats=[Rune.STAT_SPD], substat_values=[0])
        self.assertTrue(rune.has_speed)

    def test_has_resistance(self):
        rune = Rune.stub(substats=[Rune.STAT_RESIST_PCT], substat_values=[0])
        self.assertTrue(rune.has_resist)

    def test_has_accurracy(self):
        rune = Rune.stub(substats=[Rune.STAT_ACCURACY_PCT], substat_values=[0])
        self.assertTrue(rune.has_accuracy)

    def test_main_stat_sets_has_flag(self):
        rune = Rune.stub(main_stat=Rune.STAT_HP)
        self.assertTrue(rune.has_hp)

    def test_innate_stat_sets_has_flag(self):
        rune = Rune.stub(innate_stat=Rune.STAT_HP, innate_stat_value=8)
        self.assertTrue(rune.has_hp)

    def test_substat_stat_sets_has_flag(self):
        rune = Rune.stub(substats=[Rune.STAT_HP], substat_values=[0])
        self.assertTrue(rune.has_hp)

    def test_get_stat_from_main_stat(self):
        rune = Rune.stub(
            level=0,
            stars=6,
            main_stat=Rune.STAT_HP,
            main_stat_value=Rune.MAIN_STAT_VALUES[Rune.STAT_HP][6][0],
        )
        self.assertEqual(rune.get_stat(Rune.STAT_HP), Rune.MAIN_STAT_VALUES[Rune.STAT_HP][6][0])

    def test_get_stat_from_innate_stat(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_HP,
            innate_stat_value=8,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_HP), 8)

    def test_get_stat_from_substat(self):
        rune = Rune.stub(
            substats=[Rune.STAT_HP],
            substat_values=[8],
        )
        rune.clean()
        self.assertEqual(rune.get_stat(Rune.STAT_HP), 8)

    def test_get_hp_pct(self):
        rune = Rune.stub(
            main_stat=Rune.STAT_ATK_PCT,
            innate_stat=Rune.STAT_HP_PCT,
            innate_stat_value=8,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_HP_PCT), 8)

    def test_get_hp(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_HP,
            innate_stat_value=8,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_HP), 8)

    def test_get_atk_pct(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_ATK_PCT,
            innate_stat_value=8,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_ATK_PCT), 8)

    def test_get_atk(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_ATK,
            innate_stat_value=8,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_ATK), 8)

    def test_get_spd(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_SPD,
            innate_stat_value=6,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_SPD), 6)

    def test_get_cri_rate(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_CRIT_RATE_PCT,
            innate_stat_value=6,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_CRIT_RATE_PCT), 6)

    def test_get_cri_dmg(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_CRIT_DMG_PCT,
            innate_stat_value=7,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_CRIT_DMG_PCT), 7)

    def test_get_res(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_RESIST_PCT,
            innate_stat_value=8,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_RESIST_PCT), 8)

    def test_get_acc(self):
        rune = Rune.stub(
            innate_stat=Rune.STAT_ACCURACY_PCT,
            innate_stat_value=8,
        )
        self.assertEqual(rune.get_stat(Rune.STAT_ACCURACY_PCT), 8)

    def test_get_stat_with_grind_applied(self):
        rune = Rune.stub(
            substats=[Rune.STAT_ATK],
            substat_values=[4],
            substats_grind_value=[4],
        )
        self.assertEqual(rune.get_stat(Rune.STAT_ATK), 8)


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

    def test_efficiency_over_100_with_grinds(self):
        rune = Rune.stub(
            level=15,
            stars=6,
            innate_stat=Rune.STAT_ACCURACY_PCT,
            innate_stat_value=8,
            substats=[
                Rune.STAT_SPD,
                Rune.STAT_ATK_PCT,
                Rune.STAT_DEF_PCT,
                Rune.STAT_RESIST_PCT,
            ],
            substat_values=[30, 8, 8, 8],  # All upgrades into SPD
            substats_grind_value=[3, 0, 0, 0],
        )
        self.assertAlmostEqual(
            (63 / 63 + 1 * (30 + 3) / 6 * 0.2 + 4 * 1 * 0.2) / 2.8 * 100,
            rune.efficiency
        )
