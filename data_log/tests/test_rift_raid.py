from bestiary.models import GameItem
from data_log import models
from .test_log_views import BaseLogTest


class ElementalRiftBeastTests(BaseLogTest):
    fixtures = ['test_game_items', 'test_levels']

    def test_raid_log_start(self):
        response = self._do_log('BattleRiftOfWorldsRaidStart/raid_r1_3x_grindstones.json')
        self.assertEqual(response.status_code, 200)

        log = models.RiftRaidLog.objects.first()
        self.assertEqual(log.level.dungeon.category, models.Dungeon.CATEGORY_RIFT_OF_WORLDS_RAID)
        self.assertEqual(log.level.floor, 1)
        self.assertNotEqual(log.battle_key, 0)
        self.assertIsNone(log.success)
        self.assertIsNone(log.contribution_amount)

    def test_raid_log_result(self):
        self._do_log('BattleRiftOfWorldsRaidStart/raid_r1_3x_grindstones.json')
        response = self._do_log('BattleRiftOfWorldsRaidResult/raid_r1_3x_grindstones.json')
        self.assertEqual(response.status_code, 200)

        log = models.RiftRaidLog.objects.first()
        self.assertTrue(log.success)
        self.assertEqual(log.contribution_amount, 35)

    def test_raid_fail(self):
        response = self._do_log('BattleRiftOfWorldsRaidStart/raid_r4_fail_extra_placement_support.json')
        self.assertEqual(response.status_code, 200)
        response = self._do_log('BattleRiftOfWorldsRaidResult/raid_r4_fail_extra_placement_support.json')
        self.assertEqual(response.status_code, 200)

        log = models.RiftRaidLog.objects.first()
        self.assertFalse(log.success)

    def test_raid_grindstone_drop(self):
        self._do_log('BattleRiftOfWorldsRaidStart/raid_r1_3x_grindstones.json')
        self._do_log('BattleRiftOfWorldsRaidResult/raid_r1_3x_grindstones.json')

        log = models.RiftRaidLog.objects.first()
        self.assertEqual(log.runecrafts.count(), 3)

    def test_raid_mana_drop(self):
        self._do_log('BattleRiftOfWorldsRaidStart/raid_r1_mana_2x_grindstone.json')
        self._do_log('BattleRiftOfWorldsRaidResult/raid_r1_mana_2x_grindstone.json')

        log = models.RiftRaidLog.objects.first()
        self.assertEqual(log.items.count(), 1)
        self.assertEqual(log.items.first().item.category, GameItem.CATEGORY_CURRENCY)

    def test_raid_extra_placement(self):
        self._do_log('BattleRiftOfWorldsRaidStart/raid_r2_grindstone_extra_placement_support.json')
        self._do_log('BattleRiftOfWorldsRaidResult/raid_r2_grindstone_extra_placement_support.json')

        log = models.RiftRaidLog.objects.first()
        # Total of 2 drops due to extra placement. One drop is social points
        self.assertEqual(log.runecrafts.count(), 1)
        self.assertEqual(log.items.count(), 1)
        self.assertEqual(log.items.first().item.category, GameItem.CATEGORY_CURRENCY)
        self.assertEqual(log.items.first().item.com2us_id, 2)
        self.assertEqual(log.items.first().quantity, 20)

    def test_two_people_logging_same_raid(self):
        self._do_log('BattleRiftOfWorldsRaidStart/raid_r1_3x_grindstones.json')
        self._do_log('BattleRiftOfWorldsRaidStart/raid_r1_3x_grindstones_second_wizard.json')

        self._do_log('BattleRiftOfWorldsRaidResult/raid_r1_3x_grindstones.json')
        self._do_log('BattleRiftOfWorldsRaidResult/raid_r1_3x_grindstones_second_wizard.json')

        # First log has drop for own drop and third person
        log1 = models.RiftRaidLog.objects.get(wizard_id=123)
        self.assertEqual(log1.runecrafts.count(), 2)

        # Second log has drop for self only
        log2 = models.RiftRaidLog.objects.get(wizard_id=258)
        self.assertEqual(log2.runecrafts.count(), 1)
