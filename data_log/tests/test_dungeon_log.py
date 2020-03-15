from bestiary.models import Level, GameItem
from data_log import models
from .test_log_views import BaseLogTest


class CairosLogTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels', 'test_summon_monsters']

    def test_dungeon_result(self):
        self._do_log('BattleDungeonResult_V2/giants_b10_rune_drop.json')

        self.assertEqual(models.DungeonLog.objects.count(), 1)

        log = models.DungeonLog.objects.first()
        self.assertIsNotNone(log.success)
        self.assertIsNotNone(log.clear_time)

    def test_level_parsed_correctly(self):
        self._do_log('BattleDungeonResult_V2/giants_b5_unknown_scroll.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 8001)
        self.assertEqual(log.level.floor, 5)

        self._do_log('BattleDungeonResult_V2/dragon_b10_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 9001)
        self.assertEqual(log.level.floor, 10)

        self._do_log('BattleDungeonResult_V2/hall_of_dark_small_essence_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 1001)
        self.assertEqual(log.level.floor, 10)

    def test_dungeon_failed(self):
        self._do_log('BattleDungeonResult_V2/giants_b10_failed.json')
        log = models.DungeonLog.objects.first()
        self.assertFalse(log.success)

    def test_dungeon_success(self):
        self._do_log('BattleDungeonResult_V2/giants_b10_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertTrue(log.success)

    def test_dungeon_rune_drop(self):
        self._do_log('BattleDungeonResult_V2/giants_b10_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.runes.count(), 1)

    def test_dungeon_item_drop(self):
        self._do_log('BattleDungeonResult_V2/giants_b10_harmony_drop.json')
        log = models.DungeonLog.objects.first()
        # Expect Mana, Energy, Crystal, and Craft Item
        self.assertEqual(log.items.count(), 4)
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=1).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=102).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=103).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CRAFT_STUFF, item__com2us_id=4001).exists())

    def test_hoh_ignored(self):
        self._do_log('BattleDungeonResult_V2/hoh_light_rakshasa.json')
        log = models.DungeonLog.objects.first()
        self.assertIsNone(log)

    def test_essence_drop(self):
        self._do_log('BattleDungeonResult_V2/hall_of_dark_small_essence_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.items.filter(item__category=GameItem.CATEGORY_ESSENCE).count(), 1)
        item_drop = log.items.filter(item__category=GameItem.CATEGORY_ESSENCE).first()
        self.assertEqual(item_drop.item.com2us_id, 11005)
        self.assertEqual(item_drop.quantity, 5)

    def test_summon_scroll_drop(self):
        self._do_log('BattleDungeonResult_V2/giants_b5_unknown_scroll.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.items.filter(item__category=GameItem.CATEGORY_SUMMON_SCROLL).count(), 1)
        item_drop = log.items.filter(item__category=GameItem.CATEGORY_SUMMON_SCROLL).first()
        self.assertEqual(item_drop.item.com2us_id, 1)
        self.assertEqual(item_drop.quantity, 7)

    def test_secret_dungeon_drop(self):
        self._do_log('BattleDungeonResult_V2/hall_of_light_b1_howl_secret_dungeon_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.secret_dungeons.count(), 1)
        sd_drop = log.secret_dungeons.first()
        self.assertEqual(sd_drop.level.dungeon.com2us_id, 1051)

    def test_monster_drop(self):
        self._do_log('BattleDungeonResult_V2/giants_b5_rainbowmon_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.monsters.count(), 1)


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
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 1)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_NORMAL)
        self.assertEqual(log.level.floor, 1)

        self._do_log('BattleScenarioStart/kabir_ruins_hard_b1.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 3)
        self.assertEqual(log.level.difficulty, Level.DIFFICULTY_HARD)
        self.assertEqual(log.level.floor, 1)

        self._do_log('BattleScenarioStart/faimon_hell_b3.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.level.dungeon.com2us_id, 9)
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


class DimensionHoleTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels']

    def test_dungeon_result(self):
        self._do_log('BattleDimensionHoleDungeonResult/beast_men_b1_rune_drop.json')
        self.assertEqual(models.DungeonLog.objects.count(), 1)
        log = models.DungeonLog.objects.first()
        self.assertIsNotNone(log.success)
        self.assertIsNotNone(log.clear_time)

    def test_practice_not_logged(self):
        self._do_log('BattleDimensionHoleDungeonResult/ellunia_b1_practice.json')
        self.assertEqual(models.DungeonLog.objects.count(), 0)

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

    def test_dungeon_failed(self):
        self._do_log('BattleDungeonResult_V2/giants_b10_failed.json')
        log = models.DungeonLog.objects.first()
        self.assertFalse(log.success)

    def test_failed(self):
        self._do_log('BattleDimensionHoleDungeonResult/sanctuary_b4_failed.json')
        log = models.DungeonLog.objects.first()
        self.assertFalse(log.success)

    def test_ancient_rune_drop(self):
        self._do_log('BattleDimensionHoleDungeonResult/beast_men_b1_rune_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.runes.count(), 1)
        rune = log.runes.first()
        self.assertTrue(rune.ancient)

    def test_item_drop(self):
        self._do_log('BattleDimensionHoleDungeonResult/ellunia_b3_rune_ore_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.items.count(), 2)
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CURRENCY, item__com2us_id=102).exists())
        self.assertTrue(log.items.filter(item__category=GameItem.CATEGORY_CRAFT_STUFF, item__com2us_id=9002).exists())

    def test_ancient_enchant_gem_drop(self):
        self._do_log('BattleDimensionHoleDungeonResult/sanctuary_b5_gem_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.rune_crafts.count(), 1)
        craft = log.rune_crafts.first()
        self.assertEqual(craft.type, models.DungeonRuneCraftDrop.CRAFT_ANCIENT_GEM)

    def test_ancient_grindstone_drop(self):
        self._do_log('BattleDimensionHoleDungeonResult/sanctuary_b5_grind_drop.json')
        log = models.DungeonLog.objects.first()
        self.assertEqual(log.rune_crafts.count(), 1)
        craft = log.rune_crafts.first()
        self.assertEqual(craft.type, models.DungeonRuneCraftDrop.CRAFT_ANCIENT_GRINDSTONE)
