from data_log import models
from .test_log_views import BaseLogTest


class WorldBossTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels', 'test_world_boss_monsters']

    def test_world_boss_log_start(self):
        response = self._do_log('BattleWorldBossStart/world_boss_start_a_mana_mystical_essence.json')
        self.assertEqual(response.status_code, 200)

        self.assertEqual(models.WorldBossLog.objects.count(), 1)
        log = models.WorldBossLog.objects.first()
        self.assertEqual(log.level.dungeon.category, models.Dungeon.CATEGORY_WORLD_BOSS)
        self.assertEqual(log.battle_key, 1)
        self.assertEqual(log.grade, models.WorldBossLog.GRADE_A)
        self.assertEqual(log.damage, 1470200)
        self.assertEqual(log.battle_points, 144544)
        self.assertEqual(log.bonus_battle_points, 4739)
        self.assertEqual(log.avg_monster_level, 40.0)
        self.assertEqual(log.monster_count, 20)

    def test_world_boss_log_item_drop(self):
        self._do_log('BattleWorldBossStart/world_boss_start_a_mana_mystical_essence.json')
        log = models.WorldBossLog.objects.first()
        self.assertEqual(log.items.count(), 7)

    def test_world_boss_log_rune_drop(self):
        self._do_log('BattleWorldBossStart/world_boss_b_plus_mana_essence_rune.json')
        log = models.WorldBossLog.objects.first()
        self.assertEqual(log.runes.count(), 0)

        response = self._do_log('BattleWorldBossResult/world_boss_b_plus_mana_essence_rune.json')
        self.assertEqual(response.status_code, 200)

        log = models.WorldBossLog.objects.first()
        self.assertEqual(log.runes.count(), 1)

    def test_world_boss_monster_drop(self):
        self._do_log('BattleWorldBossStart/world_boss_a_plus_king_angelmon.json')
        log = models.WorldBossLog.objects.first()
        self.assertEqual(log.monsters.count(), 1)
