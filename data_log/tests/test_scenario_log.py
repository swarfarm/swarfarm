from rest_framework.test import APIRequestFactory

from bestiary.models import Dungeon, Level
from data_log import models
from .test_log_views import BaseLogTest


class ScenarioLogTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels']

    def test_scenario_start(self):
        self._do_log('ScenarioBattleStart/garen_normal_rune_drop.json')

        self.assertEqual(models.DungeonLog.objects.count(), 1)

        log = models.DungeonLog.objects.first()
        self.assertEqual(log.battle_key, 1)
        self.assertIsNone(log.success)

    def test_normal_difficulty_scenario_start(self):
        self._do_log('ScenarioBattleStart/garen_normal_rune_drop.json')

        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level, Level.objects.get(
            dungeon__pk=1,
            floor=1,
            difficulty=Level.DIFFICULTY_NORMAL,
        ))

    def test_hard_difficulty_scenario_start(self):
        self._do_log('ScenarioBattleStart/kabir_hard_rune_drop.json')

        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level, Level.objects.get(
            dungeon__pk=3,
            floor=1,
            difficulty=Level.DIFFICULTY_HARD,
        ))

    def test_hell_difficulty_scenario_start(self):
        self._do_log('ScenarioBattleStart/faimon_hell_rune_drop.json')

        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level, Level.objects.get(
            dungeon__pk=9,
            floor=3,
            difficulty=Level.DIFFICULTY_HELL,
        ))

    def test_scenario_result(self):
        self._do_log('ScenarioBattleStart/garen_normal_rune_drop.json')
        self._do_log('ScenarioBattleResult/garen_normal_rune_drop.json')

        # Updated same log entry created in ScenarioBattleStart
        self.assertEqual(models.DungeonLog.objects.count(), 1)

        log = models.DungeonLog.objects.first()
        self.assertIsNotNone(log.success)
        self.assertIsNotNone(log.clear_time)

    def test_scenario_rune_drop(self):
        self._do_log('ScenarioBattleStart/garen_normal_rune_drop.json')
        self._do_log('ScenarioBattleResult/garen_normal_rune_drop.json')

        log = models.DungeonLog.objects.first()
        rune = models.DungeonRuneDrop.objects.first()
        self.assertEqual(rune.log, log)