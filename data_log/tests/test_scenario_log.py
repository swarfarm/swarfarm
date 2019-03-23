from bestiary.models import Level, GameItem
from data_log import models
from .test_log_views import BaseLogTest


class ScenarioLogTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels', 'test_summon_monsters']

    def test_scenario_start(self):
        self._do_log('BattleScenarioStart/garen_normal_b1.json')
        self.assertEqual(models.DungeonLog.objects.count(), 1)
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.battle_key, 1)
        self.assertIsNone(log.success)

    def test_scenario_result(self):
        self._do_log('BattleScenarioStart/garen_normal_b1.json')
        self._do_log('BattleScenarioResult/garen_normal_rune_drop.json')
        self.assertEqual(models.DungeonLog.objects.count(), 1)
        log = models.DungeonLog.objects.first()
        self.assertIsNotNone(log.success)
        self.assertIsNotNone(log.clear_time)

    def test_level_parsed_correctly(self):
        self._do_log('BattleScenarioStart/garen_normal_b1.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.pk, 1)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_NORMAL)
        self.assertEqual(log.level.floor, 1)

        self._do_log('BattleScenarioStart/kabir_ruins_hard_b1.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.pk, 3)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_HARD)
        self.assertEqual(log.level.floor, 1)

        self._do_log('BattleScenarioStart/faimon_hell_b3.json')
        log = models.DungeonLog.objects.last()
        self.assertEqual(log.level.dungeon.pk, 9)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_HELL)
        self.assertEqual(log.level.floor, 3)

    def test_scenario_failed(self):
        self._do_log('BattleScenarioStart/garen_normal_b1.json')
        self._do_log('BattleScenarioResult/garen_normal_failed.json')
        log = models.DungeonLog.objects.first()
        self.assertFalse(log.success)

    def test_scenario_success(self):
        self._do_log('BattleScenarioStart/garen_normal_b1.json')
        self._do_log('BattleScenarioResult/garen_normal_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertTrue(log.success)

    def test_scenario_rune_drop(self):
        self._do_log('BattleScenarioStart/garen_normal_b1.json')
        self._do_log('BattleScenarioResult/garen_normal_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.runes.count(), 1)

    def test_scenario_monster_drop(self):
        self._do_log('BattleScenarioStart/faimon_hell_b1.json')
        self._do_log('BattleScenarioResult/faimon_hell_monster_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.monsters.count(), 1)

    def test_scenario_item_drop(self):
        self._do_log('BattleScenarioStart/faimon_hell_b1.json')
        self._do_log('BattleScenarioResult/faimon_hell_craft_drop.json')
        log = models.DungeonLog.objects.first()
        # Expect Mana, Energy, and Craft Item
        self.assertEqual(log.items.count(), 3)
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=102).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=103).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CRAFT_STUFF, item__com2us_id=1003).exists())
