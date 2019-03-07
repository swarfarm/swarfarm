from bestiary.models import Level, GameItem
from data_log import models
from .test_log_views import BaseLogTest


class ScenarioLogTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels', 'test_summon_monsters']

    def test_scenario_result(self):
        self._do_log('BattleScenarioResult/garen_normal_rune_drop.json')

        self.assertEqual(models.DungeonLog.objects.count(), 1)

        log = models.DungeonLog.objects.first()
        self.assertIsNotNone(log.success)
        self.assertIsNotNone(log.clear_time)

    def test_level_parsed_correctly(self):
        self._do_log('BattleScenarioResult/garen_normal_rune_drop.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.pk, 1)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_NORMAL)
        self.assertEqual(log.level.floor, 1)

        self._do_log('BattleScenarioResult/kabir_hard_rune_drop.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.pk, 3)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_HARD)
        self.assertEqual(log.level.floor, 1)

        self._do_log('BattleScenarioResult/faimon_hell_craft_drop.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.pk, 9)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_HELL)
        self.assertEqual(log.level.floor, 4)

    def test_scenario_rune_drop(self):
        self._do_log('BattleScenarioResult/garen_normal_rune_drop.json')

        log = models.DungeonLog.objects.first()
        self.assertEqual(log.dungeonrunedrop_set.count(), 1)

    def test_scenario_monster_drop(self):
        self._do_log('BattleScenarioResult/faimon_hell_monster_drop.json')

        log = models.DungeonLog.objects.first()
        self.assertEqual(log.dungeonmonsterdrop_set.count(), 1)

    def test_scenario_item_drop(self):
        self._do_log('BattleScenarioResult/faimon_hell_craft_drop.json')

        log = models.DungeonLog.objects.first()
        # Expect Mana, Energy, and Craft Item
        self.assertEqual(log.dungeonitemdrop_set.count(), 3)
        self.assertTrue(log.dungeonitemdrop_set.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=102).exists())
        self.assertTrue(log.dungeonitemdrop_set.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=103).exists())
        self.assertTrue(log.dungeonitemdrop_set.filter(item__category=GameItem.CATEGORY_CRAFT_STUFF, item__com2us_id=1003).exists())