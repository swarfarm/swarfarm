from bestiary.models import GameItem
from data_log import models
from .test_log_views import BaseLogTest


class DimensionHoleTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels']

    def test_dungeon_result(self):
        self._do_log('BattleDimensionHoleDungeonResult/beast_men_b1_rune_drop.json')
        self.assertEqual(models.DungeonLog.objects.count(), 1)
        log = models.DungeonLog.objects.first()
        self.assertIsNotNone(log.success)
        self.assertIsNotNone(log.clear_time)

    def test_level_parsed_correctly(self):
        self._do_log('BattleDimensionHoleDungeonResult/beast_men_b1_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 3101)
        self.assertEqual(log.level.floor, 1)

        self._do_log('BattleDimensionHoleDungeonResult/ellunia_b3_rune_ore_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 1202)
        self.assertEqual(log.level.floor, 3)

        self._do_log('BattleDimensionHoleDungeonResult/sanctuary_b2_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 1101)
        self.assertEqual(log.level.floor, 2)

    def test_success(self):
        self._do_log('BattleDimensionHoleDungeonResult/ellunia_b3_rune_ore_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertTrue(log.success)

    def test_fail(self):
        # TODO: Get failure log to test with
        pass

    def test_ancient_rune_drop(self):
        self._do_log('BattleDimensionHoleDungeonResult/beast_men_b1_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.runes.count(), 1)

    def test_item_drop(self):
        self._do_log('BattleDimensionHoleDungeonResult/ellunia_b3_rune_ore_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.items.count(), 2)
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=102).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CRAFT_STUFF, item__com2us_id=9002).exists())

    def test_ancient_grindstone_drop(self):
        # TODO: Get grindstone drop log to test with
        pass

    def test_ancient_enchant_gem_drop(self):
        # TODO: Get grindstone drop log to test with
        pass