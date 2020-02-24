import json

from django.test import TestCase

from bestiary import models
from bestiary.parse.dungeons import scenario_waves, dungeon_waves


class ScenarioWaveParse(TestCase):
    fixtures = ['test_levels', 'test_dungeon_wave_monsters']

    def test_number_of_waves(self):
        scenario_waves(battle_scenario_start)
        level = models.Level.objects.get(
            dungeon__category=models.Dungeon.CATEGORY_SCENARIO,
            dungeon__com2us_id=9,
            floor=1,
            difficulty=models.Level.DIFFICULTY_HELL
        )
        self.assertEqual(level.wave_set.count(), 3)

    def test_number_of_enemies(self):
        scenario_waves(battle_scenario_start)
        level = models.Level.objects.get(
            dungeon__category=models.Dungeon.CATEGORY_SCENARIO,
            dungeon__com2us_id=9,
            floor=1,
            difficulty=models.Level.DIFFICULTY_HELL
        )

        num_enemies = [wave.enemy_set.count() for wave in level.wave_set.all()]
        self.assertEqual(num_enemies, [4, 4, 5])

    def test_enemy_stats(self):
        scenario_waves(battle_scenario_start)
        level = models.Level.objects.get(
            dungeon__category=models.Dungeon.CATEGORY_SCENARIO,
            dungeon__com2us_id=9,
            floor=1,
            difficulty=models.Level.DIFFICULTY_HELL
        )

        enemy = level.wave_set.first().enemy_set.first()

        self.assertEqual(enemy.com2us_id, 3)
        self.assertEqual(enemy.monster.com2us_id, 13305)
        self.assertFalse(enemy.boss)
        self.assertEqual(enemy.stars, 4)
        self.assertEqual(enemy.level, 40)
        self.assertEqual(enemy.hp, 8895)
        self.assertEqual(enemy.attack, 753)
        self.assertEqual(enemy.defense, 536)
        self.assertEqual(enemy.speed, 126)
        self.assertEqual(enemy.resist, 24)
        self.assertEqual(enemy.accuracy_bonus, 0)
        self.assertEqual(enemy.crit_bonus, 0)
        self.assertEqual(enemy.crit_damage_reduction, 0)


class DungeonWaveParse(TestCase):
    fixtures = ['test_levels', 'test_dungeon_wave_monsters']

    def test_number_of_waves(self):
        dungeon_waves(battle_dungeon_start)
        level = models.Level.objects.get(
            dungeon__category=models.Dungeon.CATEGORY_CAIROS,
            dungeon__com2us_id=1001,
            floor=10,
        )
        self.assertEqual(level.wave_set.count(), 3)

    def test_number_of_enemies(self):
        dungeon_waves(battle_dungeon_start)
        level = models.Level.objects.get(
            dungeon__category=models.Dungeon.CATEGORY_CAIROS,
            dungeon__com2us_id=1001,
            floor=10,
        )

        num_enemies = [wave.enemy_set.count() for wave in level.wave_set.all()]
        self.assertEqual(num_enemies, [5, 5, 3])

    def test_enemy_stats(self):
        dungeon_waves(battle_dungeon_start)
        level = models.Level.objects.get(
            dungeon__category=models.Dungeon.CATEGORY_CAIROS,
            dungeon__com2us_id=1001,
            floor=10,
        )

        enemy = level.wave_set.first().enemy_set.first()

        self.assertEqual(enemy.com2us_id, 4078)
        self.assertEqual(enemy.monster.com2us_id, 211006)
        self.assertFalse(enemy.boss)
        self.assertEqual(enemy.stars, 1)
        self.assertEqual(enemy.level, 62)
        self.assertEqual(enemy.hp, 27420)
        self.assertEqual(enemy.attack, 812)
        self.assertEqual(enemy.defense, 974)
        self.assertEqual(enemy.speed, 67)
        self.assertEqual(enemy.resist, 25)
        self.assertEqual(enemy.accuracy_bonus, 0)
        self.assertEqual(enemy.crit_bonus, 0)
        self.assertEqual(enemy.crit_damage_reduction, 0)


battle_scenario_start = json.loads("""
{
  "request": {
    "command": "BattleScenarioStart",
    "region_id": 9,
    "stage_no": 1,
    "difficulty": 3
  },
  "response": {
    "command": "BattleScenarioStart",
    "opp_unit_list": [
      [
        {
          "unit_id": 3,
          "unit_master_id": 13305,
          "unit_level": 40,
          "size_scale": 100,
          "class": 4,
          "con": 593,
          "atk": 753,
          "def": 536,
          "spd": 126,
          "resist": 24,
          "attribute": 5,
          "boss": 0
        },
        {
          "unit_id": 1,
          "unit_master_id": 13302,
          "unit_level": 40,
          "size_scale": 100,
          "class": 4,
          "con": 673,
          "atk": 673,
          "def": 536,
          "spd": 126,
          "resist": 24,
          "attribute": 2,
          "boss": 0
        },
        {
          "unit_id": 2,
          "unit_master_id": 13305,
          "unit_level": 40,
          "size_scale": 100,
          "class": 4,
          "con": 593,
          "atk": 753,
          "def": 536,
          "spd": 126,
          "resist": 24,
          "attribute": 5,
          "boss": 0
        },
        {
          "unit_id": 4,
          "unit_master_id": 13302,
          "unit_level": 40,
          "size_scale": 100,
          "class": 4,
          "con": 673,
          "atk": 673,
          "def": 536,
          "spd": 126,
          "resist": 24,
          "attribute": 2,
          "boss": 0
        }
      ],
      [
        {
          "unit_id": 7,
          "unit_master_id": 13302,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 824,
          "atk": 824,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 2,
          "boss": 0
        },
        {
          "unit_id": 5,
          "unit_master_id": 13305,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 726,
          "atk": 921,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 5,
          "boss": 0
        },
        {
          "unit_id": 6,
          "unit_master_id": 13302,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 824,
          "atk": 824,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 2,
          "boss": 0
        },
        {
          "unit_id": 8,
          "unit_master_id": 13305,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 726,
          "atk": 921,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 5,
          "boss": 0
        }
      ],
      [
        {
          "unit_id": 13,
          "unit_master_id": 13302,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 824,
          "atk": 824,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 2,
          "boss": 0
        },
        {
          "unit_id": 11,
          "unit_master_id": 13302,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 824,
          "atk": 824,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 2,
          "boss": 0
        },
        {
          "unit_id": 9,
          "unit_master_id": 13312,
          "unit_level": 40,
          "size_scale": 150,
          "class": 6,
          "con": 1314,
          "atk": 1440,
          "def": 1001,
          "spd": 137,
          "resist": 27,
          "attribute": 2,
          "boss": 0
        },
        {
          "unit_id": 10,
          "unit_master_id": 13305,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 726,
          "atk": 921,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 5,
          "boss": 0
        },
        {
          "unit_id": 12,
          "unit_master_id": 13305,
          "unit_level": 40,
          "size_scale": 100,
          "class": 5,
          "con": 726,
          "atk": 921,
          "def": 656,
          "spd": 126,
          "resist": 24,
          "attribute": 5,
          "boss": 0
        }
      ]
    ]
  }
}
""")

battle_dungeon_start = json.loads("""
{
  "request": {
    "command": "BattleDungeonStart",
    "dungeon_id": 1001,
    "stage_id": 10
  },
  "response": {
    "command": "BattleDungeonStart",
    "dungeon_unit_list": [
      [
        {
          "unit_id": 4078,
          "unit_master_id": 211006,
          "unit_level": 62,
          "class": 1,
          "con": 1828,
          "atk": 812,
          "def": 974,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4079,
          "unit_master_id": 211006,
          "unit_level": 62,
          "class": 1,
          "con": 1828,
          "atk": 812,
          "def": 974,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4080,
          "unit_master_id": 11405,
          "unit_level": 62,
          "class": 6,
          "con": 829,
          "atk": 518,
          "def": 874,
          "spd": 88,
          "resist": 15,
          "runes": [],
          "attribute": 5,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4081,
          "unit_master_id": 211006,
          "unit_level": 62,
          "class": 1,
          "con": 1828,
          "atk": 812,
          "def": 974,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4082,
          "unit_master_id": 211006,
          "unit_level": 62,
          "class": 1,
          "con": 1828,
          "atk": 812,
          "def": 974,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        }
      ],
      [
        {
          "unit_id": 4083,
          "unit_master_id": 211006,
          "unit_level": 65,
          "class": 1,
          "con": 2119,
          "atk": 942,
          "def": 1130,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4084,
          "unit_master_id": 211006,
          "unit_level": 65,
          "class": 1,
          "con": 2119,
          "atk": 942,
          "def": 1130,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4085,
          "unit_master_id": 11405,
          "unit_level": 65,
          "class": 6,
          "con": 864,
          "atk": 540,
          "def": 910,
          "spd": 88,
          "resist": 15,
          "runes": [],
          "attribute": 5,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4086,
          "unit_master_id": 211006,
          "unit_level": 65,
          "class": 1,
          "con": 2119,
          "atk": 942,
          "def": 1130,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 4087,
          "unit_master_id": 211006,
          "unit_level": 65,
          "class": 1,
          "con": 2119,
          "atk": 942,
          "def": 1130,
          "spd": 67,
          "resist": 25,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        }
      ],
      [
        {
          "unit_id": 509,
          "unit_master_id": 60105,
          "unit_level": 65,
          "class": 6,
          "con": 15425,
          "atk": 2727,
          "def": 1630,
          "spd": 114,
          "resist": 75,
          "runes": [],
          "attribute": 5,
          "boss": 1,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 5019,
          "unit_master_id": 101456,
          "unit_level": 65,
          "class": 1,
          "con": 41448,
          "atk": 942,
          "def": 1083,
          "spd": 84,
          "resist": 45,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        },
        {
          "unit_id": 5020,
          "unit_master_id": 101456,
          "unit_level": 65,
          "class": 1,
          "con": 41448,
          "atk": 942,
          "def": 1083,
          "spd": 84,
          "resist": 45,
          "runes": [],
          "attribute": 6,
          "boss": 0,
          "hit_bonus": 0,
          "critical_bonus": 0,
          "size_scale": 100,
          "crit_damage_reduction": 0,
          "special": [],
          "add_skills": [],
          "costume_id": 0
        }
      ]
    ]
  }
}
""")
