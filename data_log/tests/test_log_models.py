from django.test import TestCase

from bestiary.models import GameItem
from data_log import models


class LogEntryTests(TestCase):
    # Testing LogEntry model using a concrete subclass
    def test_parse_common_log_data(self):
        log = models.SummonLog()
        log.parse_common_log_data({
            'request': {'wizard_id': 123},
            'response': {
                'tzone': 'America/Los_Angeles',
                'tvalue': 1551746385,
            }
        })

        self.assertEqual(log.wizard_id, 123)
        self.assertEqual(log.timestamp.year, 2019)
        self.assertEqual(log.timestamp.month, 3)
        self.assertEqual(log.timestamp.day, 5)
        self.assertEqual(log.timestamp.hour, 0)
        self.assertEqual(log.timestamp.minute, 39)
        self.assertEqual(log.timestamp.second, 45)
        self.assertEqual(log.timestamp.tzinfo.zone, 'GMT')


class ItemDropTests(TestCase):
    # Test ItemDrop class using a concrete subclass
    fixtures = ['test_game_items']

    def test_parse_mana_drop(self):
        log = models.DungeonItemDrop.parse('mana', 491)
        self.assertEqual(
            log.item,
            GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Mana')
        )
        self.assertEqual(log.quantity, 491)

    def test_parse_energy_drop(self):
        log = models.DungeonItemDrop.parse('energy', 5)
        self.assertEqual(
            log.item,
            GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Energy')
        )
        self.assertEqual(log.quantity, 5)

    def test_parse_crystal_drop(self):
        log = models.DungeonItemDrop.parse('crystal', 9)
        self.assertEqual(
            log.item,
            GameItem.objects.get(category=GameItem.CATEGORY_CURRENCY, name='Crystal')
        )
        self.assertEqual(log.quantity, 9)

    def test_parse_random_scroll_drop(self):
        log = models.DungeonItemDrop.parse('random_scroll', {
            'item_master_id': 1,
            'item_quantity': 3,
        })
        self.assertEqual(
            log.item,
            GameItem.objects.get(category=GameItem.CATEGORY_SUMMON_SCROLL, name='Unknown Scroll')
        )
        self.assertEqual(log.quantity, 3)

    def test_parse_material_drop(self):
        log = models.DungeonItemDrop.parse('material', {
            'item_master_id': 12005,
            'item_quantity': 4,
        })
        self.assertEqual(
            log.item,
            GameItem.objects.get(category=GameItem.CATEGORY_ESSENCE, name='Dark Mid Essence')
        )
        self.assertEqual(log.quantity, 4)

    def test_parse_craft_stuff_drop(self):
        log = models.DungeonItemDrop.parse('craft_stuff', {
            'item_master_id': 1006,
            'item_quantity': 2,
        })
        self.assertEqual(
            log.item,
            GameItem.objects.get(category=GameItem.CATEGORY_CRAFT_STUFF, name='Cloth')
        )
        self.assertEqual(log.quantity, 2)


class MonsterDropTests(TestCase):
    fixtures = ['test_summon_monsters']

    def test_parse_monster_drop(self):
        log = models.DungeonMonsterDrop.parse('unit_info',  {
            'unit_id': 13138378732,
            'wizard_id': 12234369,
            'island_id': 3,
            'pos_x': 16,
            'pos_y': 15,
            'building_id': 0,
            'unit_master_id': 14102,
            'unit_level': 1,
            'class': 3,
            'con': 61,
            'atk': 99,
            'def': 56,
            'spd': 109,
            'resist': 15,
            'accuracy': 0,
            'critical_rate': 15,
            'critical_damage': 50,
            'experience': 0,
            'exp_gained': 0,
            'exp_gain_rate': 0,
            'skills': [[1502, 1], [1507, 1]],
            'runes': [],
            'costume_master_id': 0,
            'trans_items': [],
            'attribute': 2,
            'create_time': '2019-03-05 09:37:36',
            'source': 14,
            'homunculus': 0,
            'homunculus_name': '',
        })

        self.assertEqual(
            log.monster.com2us_id,
            14102
        )
        self.assertEqual(log.grade, 3)
        self.assertEqual(log.level, 1)


class RuneDropTests(TestCase):
    # TODO
    pass