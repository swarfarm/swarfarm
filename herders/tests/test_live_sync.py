from django.contrib.auth.models import User
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from bestiary.models import Monster, GameItem, monsters
from herders import api_views, models

import json


class BaseSyncTest(TestCase):
    fixtures = ['test_game_items', 'test_summon_monsters', 'test_wish_monster']

    def setUp(self):
        self.factory = APIRequestFactory()
        self.u = User.objects.create(username='t')
        self.summoner = models.Summoner.objects.create(user=self.u, com2us_id=123)
        self.token = Token.objects.create(user=self.u)

    def _do_sync(self, log_data_filename, *args, **kwargs):
        with open(f'herders/tests/game_api_data/{log_data_filename}', 'r') as f:
            view = api_views.SyncData.as_view({'post': 'create'})
            data = json.load(f)
            request = self.factory.post(
                reverse('v2:sync-profile-list'),
                data=data,
                format='json',
                **kwargs,
            )
            return view(request)
    
    def test_not_authenticated_sync(self):
        resp = self._do_sync('BattleDimensionHoleDungeonResult_V2/beast_men_b1_rune_drop.json')
        self.assertEqual(resp.status_code, 401)

    def test_authenticated_sync(self):
        resp = self._do_sync('BattleDimensionHoleDungeonResult_V2/beast_men_b1_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_wrong_account(self):
        self.summoner.com2us_id = 100
        self.summoner.save()
        resp = self._do_sync('BattleDimensionHoleDungeonResult_V2/beast_men_b1_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 409)


class DungeonSyncTest(BaseSyncTest):
    def test_dimension_hole_rune_drop(self):
        self._do_sync('BattleDimensionHoleDungeonResult_V2/beast_men_b1_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=32514358242)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_dimension_hole_rune_grind_drop(self):
        self._do_sync('BattleDimensionHoleDungeonResult_V2/forest_b5_grind_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        rune_grinds = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=109426984)
        self.assertTrue(rune_grinds.exists())

        rune_grind = rune_grinds.first()
        self.assertIsNotNone(rune_grind)
        self.assertEqual(rune_grind.quantity, 2)

    def test_dimension_hole_rune_enchant_drop(self):
        self._do_sync('BattleDimensionHoleDungeonResult_V2/sanctuary_b5_gem_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        rune_enchants = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=112481826)
        self.assertTrue(rune_enchants.exists())

        rune_enchant = rune_enchants.first()
        self.assertIsNotNone(rune_enchant)
        self.assertEqual(rune_enchant.quantity, 1)

    def test_dimension_hole_rune_craft_drop(self):
        self._do_sync('BattleDimensionHoleDungeonResult_V2/ellunia_b3_rune_ore_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        rune_crafts = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=9002)
        self.assertTrue(rune_crafts.exists())

        rune_craft = rune_crafts.first()
        self.assertIsNotNone(rune_craft)
        self.assertEqual(rune_craft.quantity, 12)

    def test_dungeon_rune_drop(self):
        self._do_sync('BattleDungeonResult_V2/dragon_b10_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=30350462692)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_dungeon_monster_drop(self):
        self._do_sync('BattleDungeonResult_V2/giants_b5_rainbowmon_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=15177707867)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)
    
    def test_dungeon_monster_piece_drop(self):
        self._do_sync('BattleDungeonResult_V2/hoh_phantom_thief.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        monster_pieces = models.MonsterPiece.objects.filter(owner=self.summoner, monster__com2us_id=14102)
        self.assertTrue(monster_pieces.exists())

        monster_piece = monster_pieces.first()
        self.assertIsNotNone(monster_piece)
        self.assertEqual(monster_piece.pieces, 75)

    def test_dungeon_item_drop(self):
        self._do_sync('BattleDungeonResult_V2/hall_of_dark_small_essence_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=11005)
        self.assertTrue(essences.exists())

        essence = essences.first()
        self.assertIsNotNone(essence)
        self.assertEqual(essence.quantity, 207)

    def test_dungeon_artifact_drop(self):
        self._do_sync('BattleDungeonResult_V2/punisher_b5_artifact_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        artifacts = models.ArtifactInstance.objects.filter(owner=self.summoner, com2us_id=1509482)
        self.assertTrue(artifacts.exists())

        artifact = artifacts.first()
        self.assertIsNotNone(artifact)
        self.assertIsNone(artifact.assigned_to)

    def test_scenario_rune_drop(self):
        self._do_sync('BattleScenarioResult/faimon_hell_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=25151442364)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_scenario_monster_drop(self):
        self._do_sync('BattleScenarioResult/faimon_hell_monster_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=13138378732)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)

    def test_scenario_item_drop(self):
        self._do_sync('BattleScenarioResult/faimon_hell_craft_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=1003)
        self.assertTrue(essences.exists())

        essence = essences.first()
        self.assertIsNotNone(essence)
        self.assertEqual(essence.quantity, 4)

    def test_rift_item_drop(self):
        result_mapping = {
            5002: 3,
            6001: 1,
        }
        self._do_sync('BattleRiftDungeonResult/fire_beast_b.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id__in=result_mapping.keys())
        self.assertTrue(essences.exists())

        for essence in essences:
            self.assertEqual(essence.quantity, result_mapping[essence.item.com2us_id])

    def test_rift_rune_drop(self):
        self._do_sync('BattleRiftDungeonResult/fire_beast_b.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=25328315344)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_raid_grindstones_drop(self):
        self._do_sync('BattleRiftOfWorldsRaidResult/raid_r1_3x_grindstones.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        rune_crafts = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=219997106)
        self.assertTrue(rune_crafts.exists())

        rune_craft = rune_crafts.first()
        self.assertIsNotNone(rune_craft)
        self.assertEqual(rune_craft.quantity, 1)