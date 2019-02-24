from collections import OrderedDict
from unittest.mock import Mock

from django.test import TransactionTestCase

from bestiary.models import Level, Dungeon
from herders.models import Summoner, MonsterInstance
from planner import services
from . import models, serializers


def compare_python_tree(left, right, path='/'):
    if isinstance(left, dict) and isinstance(right, dict):
        if sorted(left.keys()) != sorted(right.keys()):
            raise AssertionError("Key mismatch at {}:\n{}\n{}".format(path, left.keys(), right.keys()))
        for key in left:
            compare_python_tree(left[key], right[key], '{}.{}'.format(path, key))
    elif isinstance(left, list) and isinstance(right, list):
        if len(left) != len(right):
            raise AssertionError("List length mismatch at {}:\n{}\n{}".format(path, left, right))
        for i in range(len(left)):
            compare_python_tree(left[i], right[i], '{}.{}'.format(path, i))
    else:
        if left != right:
            raise AssertionError("Element mismatch at {}\n{}\n{}".format(path, left, right))


class SerializerTests(TransactionTestCase):
    fixtures = ['bestiary_data.json', 'herder_sample.json']

    def setUp(self):
        self.summoner = Summoner.objects.all()[0]
        dungeon = Dungeon.objects.create(
            id=1,
            name='Dragon\'s Lair',
            slug='DB',
            category=Dungeon.CATEGORY_RUNE_DUNGEON,
            # monster_slots=5,
        )
        self.dungeon = Level.objects.create(
            dungeon=dungeon,
            floor=10,
            max_slots=5,
        )

    def test_get(self):
        team = models.OptimizeTeam.objects.create(
            owner=self.summoner,
            dungeon=self.dungeon,
            name='Standard Rezzer',
        )
        monsters = MonsterInstance.objects.filter(monster__name='Megan')
        megan = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
            min_hp=17000,
            min_def=700,
            min_acc=55,
        )
        monsters = MonsterInstance.objects.filter(monster__name='Belladeon')
        belladeon = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
            min_spd=190,
            min_hp=19000,
            min_def=850,
            min_acc=55,
        )
        monsters = MonsterInstance.objects.filter(monster__name='Veromos')
        veromos = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
            min_hp=19000,
            min_def=800,
            min_acc=55,
        )
        monsters = MonsterInstance.objects.filter(monster__name='Mikene')
        mikene = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
            min_hp=19000,
            min_def=800,
        )
        monsters = MonsterInstance.objects.filter(monster__name='Sigmarus')
        sigmarus = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
            leader=True,
            min_spd=110,
            min_hp=15000,
            min_def=700,
        )
        # Speed Tuning
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=belladeon,
            faster_than=veromos,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=belladeon,
            faster_than=mikene,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=belladeon,
            faster_than=sigmarus,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )

        serializer = serializers.OptimizeTeamSerializer(instance=team)
        data = serializer.data
        # depends on data in `sw.json`
        compare_python_tree(
            {
                "id": 1,
                "dungeon": OrderedDict({"id": self.dungeon.pk, "name": "Dragon's Lair - Level 10", "max_slots": 5}),
                "name": "Standard Rezzer",
                "monsters": [
                    {"monster": {"com2us_id": 12090887474, "name": "Megan", "stars": 5, "level": 35, "notes": None}, "leader": False, "min_spd": None, "min_hp": 17000, "min_def": 700, "min_res": None, "min_acc": 55, "min_crate": None, "max_crate": None,
                     "slower_than_by": []},
                    {"monster": {"com2us_id": 12086635496, "name": "Belladeon", "stars": 6, "level": 40, "notes": None}, "leader": False, "min_spd": 190, "min_hp": 19000, "min_def": 850, "min_res": None, "min_acc": 55, "min_crate": None, "max_crate": None,
                     "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12090887474}, 'amount': None}]},
                    {"monster": {"com2us_id": 12180164163, "name": "Veromos", "stars": 6, "level": 40, "notes": None}, "leader": False, "min_spd": None, "min_hp": 19000, "min_def": 800, "min_res": None, "min_acc": 55, "min_crate": None, "max_crate": None,
                     "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12086635496}, 'amount': None}]},
                    {"monster": {"com2us_id": 12348142219, "name": "Mikene", "stars": 5, "level": 35, "notes": None}, "leader": False, "min_spd": None, "min_hp": 19000, "min_def": 800, "min_res": None, "min_acc": None, "min_crate": None, "max_crate": None,
                     "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12086635496}, 'amount': None}]},
                    {"monster": {"com2us_id": 12536563997, "name": "Sigmarus", "stars": 6, "level": 40, "notes": None}, "leader": True, "min_spd": 110, "min_hp": 15000, "min_def": 700, "min_res": None, "min_acc": None, "min_crate": None, "max_crate": None,
                     "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12086635496}, 'amount': None}]},
                ]
            },
            data,
        )

    def test_post(self):
        data = {
            "name": "Test",
            "dungeon": {"id": self.dungeon.pk},
            "monsters": [
                {"monster": {"com2us_id": 12090887474, "name": "Megan", "stars": 5, "level": 35, "notes": None}, "leader": False, "min_spd": None, "min_hp": 17000, "min_def": 700, "min_res": None, "min_acc": 55, "min_crate": None, "max_crate": None,
                 "slower_than_by": []},
                {"monster": {"com2us_id": 12086635496, "name": "Belladeon", "stars": 6, "level": 40, "notes": None}, "leader": False, "min_spd": 190, "min_hp": 19000, "min_def": 850, "min_res": None, "min_acc": 55, "min_crate": None, "max_crate": None,
                 "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12090887474}, 'amount': None}]},
                {"monster": {"com2us_id": 12180164163, "name": "Veromos", "stars": 6, "level": 40, "notes": None}, "leader": False, "min_spd": None, "min_hp": 19000, "min_def": 800, "min_res": None, "min_acc": 55, "min_crate": None, "max_crate": None,
                 "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12086635496}, 'amount': None}]},
                {"monster": {"com2us_id": 12348142219, "name": "Mikene", "stars": 5, "level": 35, "notes": None}, "leader": False, "min_spd": None, "min_hp": 19000, "min_def": 800,"min_res": None, "min_acc": None, "min_crate": None, "max_crate": None,
                 "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12086635496}, 'amount': None}]},
                {"monster": {"com2us_id": 12536563997, "name": "Sigmarus", "stars": 6, "level": 40, "notes": None}, "leader": True, "min_spd": 110, "min_hp": 15000, "min_def": 700, "min_res": None, "min_acc": None, "min_crate": None, "max_crate": None,
                 "slower_than_by": [{'type': 0, 'slower_than': {'monster': 12086635496}, 'amount': None}]},
            ]
        }
        serializer = serializers.OptimizeTeamSerializer(data=data)
        mock_request = Mock()
        mock_request.user = self.summoner.user
        serializer._context['request'] = mock_request
        self.assertTrue(
            serializer.is_valid(),
            "Serializer NOT Valid:  {}".format(serializer.errors),
        )
        serializer.save()
        team = models.OptimizeTeam.objects.get(name="Test")
        self.assertEqual(
            5,
            team.monsters.count(),
        )
        self.assertEqual(
            4,
            models.SpeedTune.objects.count(),
        )


class EliminateRedundant(TransactionTestCase):
    fixtures = ['bestiary_data.json', 'herder_sample.json']

    def setUp(self):
        self.summoner = Summoner.objects.all()[0]
        dungeon = Dungeon.objects.create(
            id=1,
            name='Dragon\'s Lair',
            slug='DB',
            category=Dungeon.CATEGORY_RUNE_DUNGEON,
            # monster_slots=5,
        )
        self.dungeon = Level.objects.create(
            dungeon=dungeon,
            floor=10,
            max_slots=5,
        )

    def test_transitive_remove(self):
        team = models.OptimizeTeam.objects.create(
            owner=self.summoner,
            dungeon=self.dungeon,
            name='Standard Rezzer',
        )
        monsters = MonsterInstance.objects.filter(monster__name='Megan')
        megan = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Belladeon')
        belladeon = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Veromos')
        veromos = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        # Speed Tuning
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=belladeon,
            faster_than=veromos,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=veromos,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )

        services.eliminate_redundant_constraints(team)

        self.assertEqual(
            models.SpeedTune.objects.count(),
            2,
        )
        # still exists
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
            ).count(),
            1,
        )
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=belladeon,
                faster_than=veromos,
            ).count(),
            1,
        )
        # eliminated
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=veromos,
            ).count(),
            0,
        )

    def test_double_transitive_remove(self):
        team = models.OptimizeTeam.objects.create(
            owner=self.summoner,
            dungeon=self.dungeon,
            name='Standard Rezzer',
        )
        monsters = MonsterInstance.objects.filter(monster__name='Megan')
        megan = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Belladeon')
        belladeon = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Veromos')
        veromos = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Sigmarus')
        sig = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        # Speed Tuning
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=belladeon,
            faster_than=veromos,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=veromos,
            faster_than=sig,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=sig,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )

        services.eliminate_redundant_constraints(team)

        self.assertEqual(
            models.SpeedTune.objects.count(),
            3,
        )
        # still exists
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
            ).count(),
            1,
        )
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=belladeon,
                faster_than=veromos,
            ).count(),
            1,
        )
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=veromos,
                faster_than=sig,
            ).count(),
            1,
        )
        # eliminated
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=sig,
            ).count(),
            0,
        )

    def test_duplicate_remove(self):
        team = models.OptimizeTeam.objects.create(
            owner=self.summoner,
            dungeon=self.dungeon,
            name='Standard Rezzer',
        )
        monsters = MonsterInstance.objects.filter(monster__name='Megan')
        megan = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Belladeon')
        belladeon = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        # Speed Tuning
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )

        services.eliminate_redundant_constraints(team)

        self.assertEqual(
            models.SpeedTune.objects.count(),
            1,
        )
        # one copy exists
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
            ).count(),
            1,
        )

    def test_priority_remove(self):
        team = models.OptimizeTeam.objects.create(
            owner=self.summoner,
            dungeon=self.dungeon,
            name='Standard Rezzer',
        )
        monsters = MonsterInstance.objects.filter(monster__name='Megan')
        megan = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Belladeon')
        belladeon = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        # Speed Tuning
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_AS_LITTLE_AS_POSSIBLE,
        )
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )

        services.eliminate_redundant_constraints(team)

        self.assertEqual(
            models.SpeedTune.objects.count(),
            1,
        )
        # still exists
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
                type=models.SpeedTune.SPD_AS_LITTLE_AS_POSSIBLE,
            ).count(),
            1,
        )
        # eliminated
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
                type=models.SpeedTune.SPD_ANY_AMOUNT,
            ).count(),
            1,
        )


class EliminateRedundantMonster(TransactionTestCase):
    fixtures = ['bestiary_data.json', 'herder_sample.json']

    def setUp(self):
        self.summoner = Summoner.objects.all()[0]
        dungeon = Dungeon.objects.create(
            id=1,
            name='Dragon\'s Lair',
            slug='DB',
            category=Dungeon.CATEGORY_RUNE_DUNGEON,
            # monster_slots=5,
        )
        self.dungeon = Level.objects.create(
            dungeon=dungeon,
            floor=10,
            max_slots=5,
        )

    def test_duplicate_remove(self):
        team = models.OptimizeTeam.objects.create(
            owner=self.summoner,
            dungeon=self.dungeon,
            name='Standard Rezzer',
        )
        monsters = MonsterInstance.objects.filter(monster__name='Megan')
        megan = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Belladeon')
        belladeon = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        # Speed Tuning
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )

        services.eliminate_redundant_constraints_mon(belladeon)

        self.assertEqual(
            models.SpeedTune.objects.count(),
            1,
        )
        # one copy exists
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
            ).count(),
            1,
        )

    def test_priority_remove(self):
        team = models.OptimizeTeam.objects.create(
            owner=self.summoner,
            dungeon=self.dungeon,
            name='Standard Rezzer',
        )
        monsters = MonsterInstance.objects.filter(monster__name='Megan')
        megan = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        monsters = MonsterInstance.objects.filter(monster__name='Belladeon')
        belladeon = models.OptimizeMonster.objects.create(
            team=team,
            monster=monsters[0],
        )
        # Speed Tuning
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_AS_LITTLE_AS_POSSIBLE,
        )
        models.SpeedTune.objects.create(
            slower_than=megan,
            faster_than=belladeon,
            type=models.SpeedTune.SPD_ANY_AMOUNT,
        )

        services.eliminate_redundant_constraints_mon(belladeon)

        self.assertEqual(
            models.SpeedTune.objects.count(),
            1,
        )
        # still exists
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
                type=models.SpeedTune.SPD_AS_LITTLE_AS_POSSIBLE,
            ).count(),
            1,
        )
        # eliminated
        self.assertEqual(
            models.SpeedTune.objects.filter(
                slower_than=megan,
                faster_than=belladeon,
                type=models.SpeedTune.SPD_ANY_AMOUNT,
            ).count(),
            0,
        )
