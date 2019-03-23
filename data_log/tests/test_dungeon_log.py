from bestiary.models import Level, GameItem
from data_log import models
from .test_log_views import BaseLogTest


class CairosLogTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels', 'test_summon_monsters']

    def test_dungeon_result(self):
        self._do_log('BattleDungeonResult/giants_b10_rune_drop.json')

        self.assertEqual(models.DungeonLog.objects.count(), 1)

        log = models.DungeonLog.objects.first()
        self.assertIsNotNone(log.success)
        self.assertIsNotNone(log.clear_time)

    def test_level_parsed_correctly(self):
        self._do_log('BattleDungeonResult/giants_b10_rune_drop.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.com2us_id, 8001)
        self.assertEqual(log.level.floor, 10)

        self._do_log('BattleDungeonResult/necro_b2_rune_drop.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.com2us_id, 6001)
        self.assertEqual(log.level.floor, 2)

        self._do_log('BattleDungeonResult/dragon_b5_transcendance_x1_drop.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.com2us_id, 9001)
        self.assertEqual(log.level.floor, 5)

    def test_dungeon_failed(self):
        self._do_log('BattleDungeonResult/giants_b10_failed.json')
        log = models.DungeonLog.objects.first()
        self.assertFalse(log.success)

    def test_dungeon_success(self):
        self._do_log('BattleDungeonResult/giants_b10_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertTrue(log.success)

    def test_dungeon_rune_drop(self):
        self._do_log('BattleDungeonResult/giants_b10_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.runes.count(), 1)

    def test_dungeon_item_drop(self):
        self._do_log('BattleDungeonResult/dragon_b5_transcendance_x1_drop.json')
        log = models.DungeonLog.objects.first()
        # Expect Mana, Energy, and Craft Item
        self.assertEqual(log.items.count(), 3)
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=102).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=103).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CRAFT_STUFF, item__com2us_id=4002).exists())

    def test_hoh_ignored(self):
        self._do_log('BattleDungeonResult/hoh_b1_monster_pieces_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertIsNone(log)

    def test_parse_rune_with_grind_data(self):
        # Occasionally see runes with grind values specified as 0s for some reason.
        self._do_log('BattleDungeonResult/giants_b10_rune_drop2.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.runes.count(), 1)


    # TODO:
    # monster drop
    # secret dungeon drop
