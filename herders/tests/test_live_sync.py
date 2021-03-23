from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse
from rest_framework.test import APIRequestFactory

from bestiary.models import Monster
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


class AuthSyncTest(BaseSyncTest):
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
        resp = self._do_sync('BattleDimensionHoleDungeonResult_V2/beast_men_b1_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=32514358242)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_dimension_hole_rune_grind_drop(self):
        resp = self._do_sync('BattleDimensionHoleDungeonResult_V2/forest_b5_grind_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        rune_grinds = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=109426984)
        self.assertTrue(rune_grinds.exists())

        rune_grind = rune_grinds.first()
        self.assertIsNotNone(rune_grind)
        self.assertEqual(rune_grind.quantity, 2)

    def test_dimension_hole_rune_enchant_drop(self):
        resp = self._do_sync('BattleDimensionHoleDungeonResult_V2/sanctuary_b5_gem_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        rune_enchants = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=112481826)
        self.assertTrue(rune_enchants.exists())

        rune_enchant = rune_enchants.first()
        self.assertIsNotNone(rune_enchant)
        self.assertEqual(rune_enchant.quantity, 1)

    def test_dimension_hole_rune_craft_drop(self):
        resp = self._do_sync('BattleDimensionHoleDungeonResult_V2/ellunia_b3_rune_ore_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        rune_crafts = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=9002)
        self.assertTrue(rune_crafts.exists())

        rune_craft = rune_crafts.first()
        self.assertIsNotNone(rune_craft)
        self.assertEqual(rune_craft.quantity, 12)

    def test_dungeon_rune_drop(self):
        resp = self._do_sync('BattleDungeonResult_V2/dragon_b10_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=30350462692)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_dungeon_monster_drop(self):
        resp = self._do_sync('BattleDungeonResult_V2/giants_b5_rainbowmon_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=15177707867)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)
    
    def test_dungeon_monster_piece_drop(self):
        resp = self._do_sync('BattleDungeonResult_V2/hoh_phantom_thief.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monster_pieces = models.MonsterPiece.objects.filter(owner=self.summoner, monster__com2us_id=14102)
        self.assertTrue(monster_pieces.exists())

        monster_piece = monster_pieces.first()
        self.assertIsNotNone(monster_piece)
        self.assertEqual(monster_piece.pieces, 75)

    def test_dungeon_item_drop(self):
        resp = self._do_sync('BattleDungeonResult_V2/hall_of_dark_small_essence_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=11005)
        self.assertTrue(essences.exists())

        essence = essences.first()
        self.assertIsNotNone(essence)
        self.assertEqual(essence.quantity, 207)

    def test_dungeon_artifact_drop(self):
        resp = self._do_sync('BattleDungeonResult_V2/punisher_b5_artifact_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        artifacts = models.ArtifactInstance.objects.filter(owner=self.summoner, com2us_id=1509482)
        self.assertTrue(artifacts.exists())

        artifact = artifacts.first()
        self.assertIsNotNone(artifact)
        self.assertIsNone(artifact.assigned_to)

    def test_scenario_rune_drop(self):
        resp = self._do_sync('BattleScenarioResult/faimon_hell_rune_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=25151442364)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_scenario_monster_drop(self):
        resp = self._do_sync('BattleScenarioResult/faimon_hell_monster_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=13138378732)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)

    def test_scenario_item_drop(self):
        resp = self._do_sync('BattleScenarioResult/faimon_hell_craft_drop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
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
        resp = self._do_sync('BattleRiftDungeonResult/fire_beast_b.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id__in=result_mapping.keys())
        self.assertTrue(essences.exists())

        for essence in essences:
            self.assertEqual(essence.quantity, result_mapping[essence.item.com2us_id])

    def test_rift_rune_drop(self):
        resp = self._do_sync('BattleRiftDungeonResult/fire_beast_b.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=25328315344)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_raid_grindstones_drop(self):
        resp = self._do_sync('BattleRiftOfWorldsRaidResult/raid_r1_3x_grindstones.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        rune_crafts = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=219997106)
        self.assertTrue(rune_crafts.exists())

        rune_craft = rune_crafts.first()
        self.assertIsNotNone(rune_craft)
        self.assertEqual(rune_craft.quantity, 1)

    def test_worldboss_reward(self):
        result_mapping = {
            12003: 170,
            11002: 392,
        }
        resp = self._do_sync('BattleWorldBossResult/world_boss_result.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id__in=result_mapping.keys())
        self.assertTrue(essences.exists())

        for essence in essences:
            self.assertEqual(essence.quantity, result_mapping[essence.item.com2us_id])
        
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id__in=[25328315344, 26589504160])
        self.assertTrue(runes.exists())

        for rune in runes:
            self.assertIsNotNone(rune)
            self.assertIsNone(rune.assigned_to)

    def test_lab_rotation_clear_no_reward(self):
        resp = self._do_sync('ReceiveGuildMazeClearRewardCrate/lab_clear_box_no_sync.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        self.assertFalse(models.RuneInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.ArtifactInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.RuneCraftInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.ArtifactCraftInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MonsterInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MaterialStorage.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MonsterShrineStorage.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MonsterPiece.objects.filter(owner=self.summoner).exists())
    
    def test_siege_box_reward_only_runes(self):
        resp = self._do_sync('ReceiveGuildSiegeRewardCrate/siege_box_runes.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id__in=[35209589327, 35209589330])
        self.assertTrue(runes.exists())

        for rune in runes:
            self.assertIsNotNone(rune)
            self.assertIsNone(rune.assigned_to)
        
        self.assertFalse(models.ArtifactInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.RuneCraftInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.ArtifactCraftInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MonsterInstance.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MaterialStorage.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MonsterShrineStorage.objects.filter(owner=self.summoner).exists())
        self.assertFalse(models.MonsterPiece.objects.filter(owner=self.summoner).exists())

    def test_lab_stage_clear_reward_grind(self):
        resp = self._do_sync('pickGuildMazeBattleClearReward/lab_clear_stage_grind.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        rune_grinds = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=179407168)
        self.assertTrue(rune_grinds.exists())

        rune_grind = rune_grinds.first()
        self.assertIsNotNone(rune_grind)
        self.assertEqual(rune_grind.quantity, 1)
        
    
    def test_lab_stage_clear_reward_rune(self):
        resp = self._do_sync('pickGuildMazeBattleClearReward/lab_clear_stage_rune.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=35153348554)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_toa_60_rainbowmon(self):
        resp = self._do_sync('BattleTrialTowerResult_v2/toa_60_rainbowmon.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=17446569075)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)
        

class MiscSyncTest(BaseSyncTest):
    def test_buy_rune_from_shop(self):
        resp = self._do_sync('BuyBlackMarketItem/buy_rune_from_shop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=24026465124)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_buy_monster_from_shop(self):
        resp = self._do_sync('BuyBlackMarketItem/buy_monster_from_shop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=10856141877)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)

    def test_buy_rune_from_guild_shop(self):
        resp = self._do_sync('BuyGuildBlackMarketItem/buy_rune_from_guild_shop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=24026517599)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_buy_monster_piece_from_guild_shop(self):
        resp = self._do_sync('BuyGuildBlackMarketItem/buy_monster_piece_from_guild_shop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monster_pieces = models.MonsterPiece.objects.filter(owner=self.summoner, monster__com2us_id=14102)
        self.assertTrue(monster_pieces.exists())

        monster_piece = monster_pieces.first()
        self.assertIsNotNone(monster_piece)
        self.assertEqual(monster_piece.pieces, 40)

    def test_buy_grind_from_guild_shop(self):
        resp = self._do_sync('BuyGuildBlackMarketItem/buy_grind_from_guild_shop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        rune_grinds = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=151706129)
        self.assertTrue(rune_grinds.exists())

        rune_grind = rune_grinds.first()
        self.assertIsNotNone(rune_grind)
        self.assertEqual(rune_grind.quantity, 1)

    def test_buy_enchant_from_guild_shop(self):
        resp = self._do_sync('BuyGuildBlackMarketItem/buy_enchant_from_guild_shop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        rune_enchants = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=150055487)
        self.assertTrue(rune_enchants.exists())

        rune_enchant = rune_enchants.first()
        self.assertIsNotNone(rune_enchant)
        self.assertEqual(rune_enchant.quantity, 2)

    def test_sell_item(self):
        resp = self._do_sync('sell_inventory_item.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        item = models.MaterialStorage.objects.get(owner=self.summoner, item__com2us_id=1003)
        self.assertIsNotNone(item)
        self.assertEqual(item.quantity, 119)

    def test_wish_monster(self):
        resp = self._do_sync('DoRandomWishItem/wish_monster.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=13158397674)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)

    def test_wish_rune(self):
        resp = self._do_sync('DoRandomWishItem/wish_rune.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        runes = models.RuneInstance.objects.filter(owner=self.summoner, com2us_id=25258738053)
        self.assertTrue(runes.exists())

        rune = runes.first()
        self.assertIsNotNone(rune)
        self.assertIsNone(rune.assigned_to)

    def test_upgrade_material(self):
        result_mapping = {
            12006: 36,
            13006: 6,
        }
        resp = self._do_sync('UpgradeDowngradeMaterial/upgrade_material.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id__in=result_mapping.keys())
        self.assertTrue(essences.exists())

        for essence in essences:
            self.assertEqual(essence.quantity, result_mapping[essence.item.com2us_id])

    def test_downgrade_material(self):
        result_mapping = {
            13004: 66,
            12004: 122,
        }
        resp = self._do_sync('UpgradeDowngradeMaterial/downgrade_material.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id__in=result_mapping.keys())
        self.assertTrue(essences.exists())

        for essence in essences:
            self.assertEqual(essence.quantity, result_mapping[essence.item.com2us_id])


class MonsterSyncTest(BaseSyncTest):
    def test_monster_to_building(self):
        resp = self._do_sync('MoveUnitBuilding/monster_to_building.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=17396548050)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertTrue(monster.in_storage)

    def test_monster_from_building(self):
        resp = self._do_sync('MoveUnitBuilding/monster_from_building.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=17396548050)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertFalse(monster.in_storage)

    def test_monster_to_shrine_storage(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855864692,
            monster=base_mon,
            stars=4,
            level=1,
        )
        models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855864694,
            monster=base_mon,
            stars=4,
            level=1,
        )
        self.assertEqual(models.MonsterInstance.objects.filter(owner=self.summoner).count(), 2)

        resp = self._do_sync('ConvertUnitToFromStorage/monsters_to_shrine.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id__in=[10855864692, 10855864694])
        self.assertFalse(monsters.exists())

        shrine = models.MonsterShrineStorage.objects.filter(owner=self.summoner, item=base_mon)
        self.assertTrue(shrine.exists())
        self.assertEqual(shrine.first().quantity, 2)

    def test_monsters_from_shrine_storage_empty(self):
        base_mon = Monster.objects.get(com2us_id=14102)

        resp = self._do_sync('ConvertUnitToFromStorage/monsters_from_shrine_empty.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        shrine = models.MonsterShrineStorage.objects.filter(owner=self.summoner, item=base_mon)
        self.assertFalse(shrine.exists())
        self.assertEqual(models.MonsterInstance.objects.filter(owner=self.summoner, monster=base_mon).count(), 2)
    
    def test_monsters_from_shrine_storage(self):
        base_mon = Monster.objects.get(com2us_id=14102)

        resp = self._do_sync('ConvertUnitToFromStorage/monsters_from_shrine.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        shrine = models.MonsterShrineStorage.objects.filter(owner=self.summoner, item=base_mon)
        self.assertTrue(shrine.exists())
        self.assertEqual(shrine.first().quantity, 17)
        self.assertEqual(models.MonsterInstance.objects.filter(owner=self.summoner, monster=base_mon).count(), 2)

    def test_monster_to_material_storage(self):
        base_mon = Monster.objects.get(com2us_id=14314)
        models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855869695,
            monster=base_mon,
            stars=4,
            level=1,
        )
        models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855869683,
            monster=base_mon,
            stars=4,
            level=1,
        )
        self.assertEqual(models.MonsterInstance.objects.filter(owner=self.summoner).count(), 2)

        resp = self._do_sync('ConvertUnitToFromItem/monsters_to_material_storage.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id__in=[10855869695, 10855869683])
        self.assertFalse(monsters.exists())

        shrine = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=143140501)
        self.assertTrue(shrine.exists())
        self.assertEqual(shrine.first().quantity, 2)

    def test_monsters_from_material_storage_empty(self):
        base_mon = Monster.objects.get(com2us_id=14314)

        resp = self._do_sync('ConvertUnitToFromItem/monsters_from_material_storage_empty.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        ms = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=143140501)
        self.assertTrue(ms.exists())
        self.assertEqual(ms.first().quantity, 0)
        self.assertEqual(models.MonsterInstance.objects.filter(owner=self.summoner, monster=base_mon).count(), 2)

    def test_monsters_from_material_storage(self):
        base_mon = Monster.objects.get(com2us_id=14314)

        resp = self._do_sync('ConvertUnitToFromItem/monsters_from_material_storage.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        ms = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id=143140501)
        self.assertTrue(ms.exists())
        self.assertEqual(ms.first().quantity, 98)
        self.assertEqual(models.MonsterInstance.objects.filter(owner=self.summoner, monster=base_mon).count(), 2)

    def test_summon_monster(self):
        resp = self._do_sync('SummonUnit/scroll_mystical.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=13118224623)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)

    def test_summon_monster_blessing_pop(self):
        resp = self._do_sync('SummonUnit/scroll_mystical_blessing_pop.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner)
        self.assertFalse(monsters.exists())

    def test_summon_monster_blessing_choice(self):
        resp = self._do_sync('ConfirmSummonChoice/blessing_selection.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=14755571003)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)
        
    def test_summon_monster_from_pieces(self):
        resp = self._do_sync('SummonUnit/monster_pieces.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=10855948375)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)

        monster_pieces = models.MonsterPiece.objects.filter(owner=self.summoner, monster__com2us_id=14102)
        self.assertTrue(monster_pieces.exists())
        self.assertEqual(monster_pieces.first().pieces, 20)

    def test_summon_monster_from_pieces_all(self):
        resp = self._do_sync('SummonUnit/monster_pieces_empty.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        monsters = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=10855948375)
        self.assertTrue(monsters.exists())

        monster = monsters.first()
        self.assertIsNotNone(monster)
        self.assertIsNotNone(monster.default_build)
        self.assertIsNotNone(monster.rta_build)

        monster_pieces = models.MonsterPiece.objects.filter(owner=self.summoner, monster__com2us_id=14102)
        self.assertFalse(monster_pieces.exists())
        
    def test_awaken_unit(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855959738,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon.save()
        resp = self._do_sync('awaken_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertEqual(mon.monster, base_mon.awakens_to)

        result_mapping = {
            11004: 1,
            11006: 275,
        }
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id__in=result_mapping.keys())
        self.assertTrue(essences.exists())

        for essence in essences:
            self.assertEqual(essence.quantity, result_mapping[essence.item.com2us_id])

    def test_awaken_unit_not_existing(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        resp = self._do_sync('awaken_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mons = models.MonsterInstance.objects.filter(owner=self.summoner, com2us_id=10855959738)
        self.assertTrue(mons.exists())
        self.assertIsNotNone(mons.first())
        self.assertEqual(mons.first().monster, base_mon.awakens_to)

        result_mapping = {
            11004: 1,
            11006: 275,
        }
        essences = models.MaterialStorage.objects.filter(owner=self.summoner, item__com2us_id__in=result_mapping.keys())
        self.assertTrue(essences.exists())

        for essence in essences:
            self.assertEqual(essence.quantity, result_mapping[essence.item.com2us_id])

    def test_sell_unit(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855953452,
            monster=base_mon,
            stars=4,
            level=1,
        )
        resp = self._do_sync('sell_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        with self.assertRaises(models.MonsterInstance.DoesNotExist) as cm:
            mon.refresh_from_db()

    def test_sacrifice_unit_with_fooder_from_inventory_lvlup(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        fooders = [
            models.MonsterInstance.objects.create(
                owner=self.summoner,
                com2us_id=c2_id,
                monster=base_mon,
                stars=4,
                level=1,
            )
        for c2_id in [10855994586, ]]
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855959738,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon_lvl = 1
        resp = self._do_sync('SacrificeUnit_V3/food_from_inventory_lvlup.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertNotEqual(mon_lvl, mon.level)

        for fooder in fooders:
            with self.assertRaises(models.MonsterInstance.DoesNotExist) as cm:
                fooder.refresh_from_db()
        
    def test_sacrifice_unit_with_fooder_from_shrine_lvlup(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        fooders = [
            models.MonsterShrineStorage.objects.create(
                owner=self.summoner,
                item=base_mon,
                quantity=1
            )
        ]
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855959738,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon_lvl = 1
        resp = self._do_sync('SacrificeUnit_V3/food_from_shrine_lvlup.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertNotEqual(mon_lvl, mon.level)

        for fooder in fooders:
            with self.assertRaises(models.MonsterShrineStorage.DoesNotExist) as cm:
                fooder.refresh_from_db()

    def test_sacrifice_unit_with_fooder_from_storage_no_lvlup(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        fooders = [
            models.MonsterInstance.objects.create(
                owner=self.summoner,
                com2us_id=c2_id,
                monster=base_mon,
                stars=4,
                level=1,
            )
        for c2_id in [10855994587,]]
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10855959738,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon_lvl = 1
        resp = self._do_sync('SacrificeUnit_V3/food_from_storage_no_lvlup.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertEqual(mon_lvl, mon.level)

        for fooder in fooders:
            with self.assertRaises(models.MonsterInstance.DoesNotExist) as cm:
                fooder.refresh_from_db()

    def test_upgrade_unit(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        fooders = [
            models.MonsterShrineStorage.objects.create(
                owner=self.summoner,
                item=base_mon,
                quantity=1
            )
        ]
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10856006746,
            monster=base_mon,
            stars=4,
            level=30,
        )
        mon_stars = 4

        resp = self._do_sync('upgrade_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertEqual(mon.level, 1)
        self.assertEqual(mon_stars + 1, mon.stars)

        for fooder in fooders:
            with self.assertRaises(models.MonsterShrineStorage.DoesNotExist) as cm:
                fooder.refresh_from_db()

    def test_lock_unit(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10563022833,
            monster=base_mon,
            stars=4,
            level=30,
        )
        resp = self._do_sync('LockUnlockUnit/lock_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertTrue(mon.ignore_for_fusion)

    def test_lock_unit_not_exist(self):
        resp = self._do_sync('LockUnlockUnit/lock_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 409)

    def test_unlock_unit(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10563022833,
            monster=base_mon,
            stars=4,
            level=30,
        )
        resp = self._do_sync('LockUnlockUnit/unlock_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertFalse(mon.ignore_for_fusion)

    def test_2a_unit(self):
        base_mon = Monster.objects.get(com2us_id=14112)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10812428307,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon.save()
        resp = self._do_sync('2a_unit.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertEqual(mon.monster, base_mon.awakens_to)

    def test_levelup_unit_in_building(self):
        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=17382539199,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon_lvl = 1
        resp = self._do_sync('SacrificeUnit_V3/levelup_unit_in_building.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        mon.refresh_from_db()
        self.assertEqual(mon_lvl + 1, mon.level)


class RuneSyncTest(BaseSyncTest):
    def test_rune_upgrade_fail_unequipped(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=23370471984,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_HP_PCT,
            stars=6,
            level=4,
            quality=models.RuneInstance.QUALITY_HERO,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_HP, models.RuneInstance.STAT_CRIT_DMG_PCT, models.RuneInstance.STAT_CRIT_RATE_PCT],
            substat_values=[428, 6, 4],
            substats_enchanted=[False, False, False],
            substats_grind_value=[0, 0, 0],
        )
        rune_lvl = rune.level
        rune_mainstat = rune.main_stat_value
        rune_substats = rune.substats
        rune_substat_values = rune.substat_values
        resp = self._do_sync('UpgradeRune/fail.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        
        rune.refresh_from_db()
        self.assertEqual(rune_lvl, rune.level)
        self.assertEqual(rune_mainstat, rune.main_stat_value)
        self.assertListEqual(rune_substats, rune.substats)
        self.assertListEqual(rune_substat_values, rune.substat_values)
    
    def test_rune_upgrade_success_unequipped(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=23370471984,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_HP_PCT,
            stars=6,
            level=4,
            quality=models.RuneInstance.QUALITY_HERO,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_HP, models.RuneInstance.STAT_CRIT_DMG_PCT, models.RuneInstance.STAT_CRIT_RATE_PCT],
            substat_values=[428, 6, 4],
            substats_enchanted=[False, False, False],
            substats_grind_value=[0, 0, 0],
        )
        rune_lvl = rune.level
        rune_substats = rune.substats
        rune_substat_values = rune.substat_values

        resp = self._do_sync('UpgradeRune/success.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        
        rune.refresh_from_db()
        new_main_stat = models.RuneInstance.MAIN_STAT_VALUES[models.RuneInstance.STAT_HP_PCT][rune.stars][rune.level]
        self.assertEqual(rune_lvl + 1, rune.level)
        self.assertEqual(rune.main_stat_value, new_main_stat)
        self.assertListEqual(rune_substats, rune.substats)
        self.assertListEqual(rune_substat_values, rune.substat_values)

    def test_rune_upgrade_success_equipped(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=23370471984,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_HP_PCT,
            stars=6,
            level=4,
            quality=models.RuneInstance.QUALITY_HERO,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_HP, models.RuneInstance.STAT_CRIT_DMG_PCT, models.RuneInstance.STAT_CRIT_RATE_PCT],
            substat_values=[428, 6, 4],
            substats_enchanted=[False, False, False],
            substats_grind_value=[0, 0, 0],
        )
        rune_lvl = rune.level
        rune_substats = rune.substats
        rune_substat_values = rune.substat_values

        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=123456,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon.default_build.assign_rune(rune)

        resp = self._do_sync('UpgradeRune/success.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        
        rune.refresh_from_db()
        mon.refresh_from_db()
        new_main_stat = models.RuneInstance.MAIN_STAT_VALUES[models.RuneInstance.STAT_HP_PCT][rune.stars][rune.level]
        self.assertEqual(rune_lvl + 1, rune.level)
        self.assertEqual(rune.main_stat_value, new_main_stat)
        self.assertListEqual(rune_substats, rune.substats)
        self.assertListEqual(rune_substat_values, rune.substat_values)
        self.assertEqual(mon.default_build.hp_pct, new_main_stat)

    def test_sell_rune_multiple_unequipped(self):
        runes = [models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=c2_id,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_HP_PCT,
            stars=6,
            level=4,
            quality=models.RuneInstance.QUALITY_LEGEND,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_HP, models.RuneInstance.STAT_CRIT_DMG_PCT, models.RuneInstance.STAT_CRIT_RATE_PCT],
            substat_values=[428, 6, 4],
            substats_enchanted=[False, False, False],
            substats_grind_value=[0, 0, 0],
        ) for c2_id in [23578172095, 23514549801]]

        resp = self._do_sync('SellRune/multiple_unequipped.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        
        for rune in runes:
            with self.assertRaises(models.RuneInstance.DoesNotExist) as cm:
                rune.refresh_from_db()
    
    def test_sell_rune_single_equipped(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=23578172095,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_HP_PCT,
            stars=6,
            level=4,
            quality=models.RuneInstance.QUALITY_LEGEND,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_HP, models.RuneInstance.STAT_CRIT_DMG_PCT, models.RuneInstance.STAT_CRIT_RATE_PCT],
            substat_values=[428, 6, 4],
            substats_enchanted=[False, False, False],
            substats_grind_value=[0, 0, 0],
        )

        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=123456,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon.default_build.assign_rune(rune)

        resp = self._do_sync('SellRune/single_equipped.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        
        with self.assertRaises(models.RuneInstance.DoesNotExist) as cm:
            rune.refresh_from_db()
        mon.refresh_from_db()

        self.assertEqual(mon.default_build.hp_pct, 0)
        
        rune_grinds = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=131099962)
        self.assertFalse(rune_grinds.exists())

    def test_grind_rune_unequipped(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=15946662483,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_ATK_PCT,
            stars=6,
            level=4,
            quality=models.RuneInstance.QUALITY_LEGEND,
            innate_stat=models.RuneInstance.STAT_HP,
            innate_stat_value=315,
            substats=[models.RuneInstance.STAT_HP, models.RuneInstance.STAT_CRIT_RATE_PCT, models.RuneInstance.STAT_ACCURACY_PCT, models.RuneInstance.STAT_SPD],
            substat_values=[21, 7, 12, 5],
            substats_enchanted=[False, True, False, False],
            substats_grind_value=[6, 0, 0, 0],
        )
        
        resp = self._do_sync('GrindEnchantReapp/grind_speed_unequipped.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        rune.refresh_from_db()
        self.assertListEqual([6, 0, 0, 4], rune.substats_grind_value)

    def test_grind_rune_equipped(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=15946662483,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_ATK_PCT,
            stars=6,
            level=4,
            quality=models.RuneInstance.QUALITY_LEGEND,
            innate_stat=models.RuneInstance.STAT_HP,
            innate_stat_value=315,
            substats=[models.RuneInstance.STAT_HP, models.RuneInstance.STAT_CRIT_RATE_PCT, models.RuneInstance.STAT_ACCURACY_PCT, models.RuneInstance.STAT_SPD],
            substat_values=[21, 7, 12, 5],
            substats_enchanted=[False, True, False, False],
            substats_grind_value=[6, 0, 0, 0],
        )

        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=123456,
            monster=base_mon,
            stars=4,
            level=1,
        )
        mon.default_build.assign_rune(rune)
        
        resp = self._do_sync('GrindEnchantReapp/grind_speed_equipped.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        rune.refresh_from_db()
        self.assertListEqual([6, 0, 0, 4], rune.substats_grind_value)
        mon.refresh_from_db()
        self.assertEqual(mon.default_build.speed, 9)  # 5 + 4 grind

        rune_grinds = models.RuneCraftInstance.objects.filter(owner=self.summoner, com2us_id=131099962)
        self.assertFalse(rune_grinds.exists())

    def test_enchant_rune(self):
        # don't check equipped/unequipped, because previous tests `test_grind_rune_(un)equipped` check that
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=23219580822,
            type=models.RuneInstance.TYPE_FOCUS,
            slot=2,
            main_stat=models.RuneInstance.STAT_ATK_PCT,
            stars=6,
            level=12,
            quality=models.RuneInstance.QUALITY_LEGEND,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_DEF_PCT, models.RuneInstance.STAT_ACCURACY_PCT, models.RuneInstance.STAT_SPD, models.RuneInstance.STAT_HP],
            substat_values=[13, 7, 17, 355],
            substats_enchanted=[False, False, False, False],
            substats_grind_value=[7, 0, 0, 0],
        )
        
        resp = self._do_sync('GrindEnchantReapp/enchant_hp_pct.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        rune.refresh_from_db()
        self.assertListEqual(rune.substats, [models.RuneInstance.STAT_DEF_PCT, models.RuneInstance.STAT_ACCURACY_PCT, models.RuneInstance.STAT_SPD, models.RuneInstance.STAT_HP_PCT])
        self.assertListEqual(rune.substat_values, [13, 7, 17, 8])
        self.assertListEqual(rune.substats_enchanted, [False, False, False, True])
        self.assertListEqual(rune.substats_grind_value, [7, 0, 0, 0])

    def test_reapp_rune_pick_old(self):
        # don't check equipped/unequipped, because previous tests `test_grind_rune_(un)equipped` check that
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=22738885100,
            type=models.RuneInstance.TYPE_REVENGE,
            slot=2,
            main_stat=models.RuneInstance.STAT_DEF_PCT,
            stars=6,
            level=12,
            quality=models.RuneInstance.QUALITY_LEGEND,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_SPD, models.RuneInstance.STAT_HP_PCT, models.RuneInstance.STAT_ATK_PCT, models.RuneInstance.STAT_DEF],
            substat_values=[15, 7, 12, 24],
            substats_enchanted=[False, False, False, False],
            substats_grind_value=[0, 0, 0, 0],
        )
        rune_substats = rune.substats
        rune_sub_vals = rune.substat_values
        rune_sub_ench = rune.substats_enchanted
        rune_sub_grinds = rune.substats_grind_value
        
        resp = self._do_sync('GrindEnchantReapp/reapp_old.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        rune.refresh_from_db()
        self.assertListEqual(rune.substats, rune_substats)
        self.assertListEqual(rune.substat_values, rune_sub_vals)
        self.assertListEqual(rune.substats_enchanted, rune_sub_ench)
        self.assertListEqual(rune.substats_grind_value, rune_sub_grinds)

    def test_reapp_rune_pick_new(self):
        # don't check equipped/unequipped, because previous tests `test_grind_rune_(un)equipped` check that
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=22738885100,
            type=models.RuneInstance.TYPE_REVENGE,
            slot=2,
            main_stat=models.RuneInstance.STAT_DEF_PCT,
            stars=6,
            level=12,
            quality=models.RuneInstance.QUALITY_LEGEND,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_SPD, models.RuneInstance.STAT_HP_PCT, models.RuneInstance.STAT_ATK_PCT, models.RuneInstance.STAT_DEF],
            substat_values=[15, 7, 12, 24],
            substats_enchanted=[False, False, False, False],
            substats_grind_value=[0, 0, 0, 0],
        )
        
        resp = self._do_sync('GrindEnchantReapp/reapp_new.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        rune.refresh_from_db()
        self.assertListEqual(rune.substats, [models.RuneInstance.STAT_HP_PCT, models.RuneInstance.STAT_CRIT_DMG_PCT, models.RuneInstance.STAT_ACCURACY_PCT, models.RuneInstance.STAT_ATK_PCT])
        self.assertListEqual(rune.substat_values, [5, 20, 12, 15])
        self.assertListEqual(rune.substats_enchanted, [False, False, False, False])
        self.assertListEqual(rune.substats_grind_value, [0, 0, 0, 0])

    def test_equip_rune_from_monster_view(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=23703327529,
            type=models.RuneInstance.TYPE_REVENGE,
            slot=5,
            main_stat=models.RuneInstance.STAT_HP,
            stars=6,
            level=0,
            quality=models.RuneInstance.QUALITY_HERO,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_RESIST_PCT, models.RuneInstance.STAT_CRIT_RATE_PCT, models.RuneInstance.STAT_SPD],
            substat_values=[4, 6, 6],
            substats_enchanted=[False, False, False],
            substats_grind_value=[0, 0, 0],
        )

        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10508978971,
            monster=base_mon,
            stars=4,
            level=28,
        )
        resp = self._do_sync('EquipUnequipRune/equip_monster_view.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        rune.refresh_from_db()
        mon.refresh_from_db()

        self.assertEqual(mon.default_build.speed, 6)

    def test_equip_rune_from_rune_management(self):
        rune = models.RuneInstance.objects.create(
            owner=self.summoner,
            com2us_id=23766273768,
            type=models.RuneInstance.TYPE_REVENGE,
            slot=5,
            main_stat=models.RuneInstance.STAT_HP,
            stars=6,
            level=0,
            quality=models.RuneInstance.QUALITY_HERO,
            innate_stat=None,
            innate_stat_value=None,
            substats=[models.RuneInstance.STAT_RESIST_PCT, models.RuneInstance.STAT_CRIT_RATE_PCT, models.RuneInstance.STAT_SPD],
            substat_values=[4, 6, 6],
            substats_enchanted=[False, False, False],
            substats_grind_value=[0, 0, 0],
        )

        base_mon = Monster.objects.get(com2us_id=14102)
        mon = models.MonsterInstance.objects.create(
            owner=self.summoner,
            com2us_id=10508978971,
            monster=base_mon,
            stars=4,
            level=28,
        )
        resp = self._do_sync('EquipUnequipRune/equip_rune_management.json', HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)

        rune.refresh_from_db()
        mon.refresh_from_db()

        # different data in test JSON, but we don't update Rune data on equip
        # so we can just use this placeholder data
        self.assertEqual(mon.default_build.speed, 6)


class ArtifactSyncTest(BaseSyncTest):
    pass
