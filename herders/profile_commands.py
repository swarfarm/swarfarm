import json

from jsonschema import Draft4Validator

from data_log.game_commands import GameApiCommand
from . import sync_schemas, sync_parser
from data_log import schemas as data_log_schemas

# Map to in-game commands and generate list of accepted API params
active_log_commands = {
    'HubUserLogin': GameApiCommand(
        sync_schemas.sync_hub_user_login_schema,
        sync_parser.sync_profile,
    ),
    'getUnitStorageList': GameApiCommand(
        sync_schemas.sync_get_unit_storage_list_schema,
        sync_parser.sync_monster_shrine,
    ),
    'BattleDungeonResult_V2': GameApiCommand(
        data_log_schemas.battle_dungeon_result_v2,
        sync_parser.sync_dungeon_reward,
    ),
    'battleInstanceResult': GameApiCommand(
        sync_schemas.sync_battle_instance_result_schema,
        sync_parser.sync_secret_dungeon_reward,
    ),
    'BattleDimensionHoleDungeonResult_v2': GameApiCommand(
        data_log_schemas.battle_dimension_hole_result_v2,
        sync_parser.sync_dungeon_reward,
    ),
    'BattleRiftDungeonResult': GameApiCommand(
        data_log_schemas.battle_rift_dungeon_result,
        sync_parser.sync_rift_reward,
    ),
    'BattleRiftOfWorldsRaidResult': GameApiCommand(
        data_log_schemas.battle_rift_of_worlds_raid_result,
        sync_parser.sync_raid_reward,
    ),
    'BattleScenarioResult': GameApiCommand(
        data_log_schemas.battle_scenario_result,
        sync_parser.sync_scenario_reward,
    ),
    'pickGuildMazeBattleClearReward': GameApiCommand(
        sync_schemas.sync_pick_guild_maze_battle_clear_reward_schema,
        sync_parser.sync_labyrinth_reward,
    ),
    # crafting
    'BuyShopItem': GameApiCommand(
        data_log_schemas.buy_shop_item,
        sync_parser.sync_buy_item,
    ),
    'BattleTrialTowerResult_v2': GameApiCommand(
        sync_schemas.sync_battle_trial_tower_result_v2_schema,
        sync_parser.sync_toa_reward,
    ),
    'BattleWorldBossResult': GameApiCommand(
        data_log_schemas.battle_world_boss_result,
        sync_parser.sync_worldboss_reward,
    ),
    'BuyGuildBlackMarketItem': GameApiCommand(
        sync_schemas.sync_buy_guild_black_market_item_schema,
        sync_parser.sync_guild_black_market_buy,
    ),
    'BuyBlackMarketItem': GameApiCommand(
        sync_schemas.sync_buy_black_market_item_schema,
        sync_parser.sync_black_market_buy,
    ),
    'MoveUnitBuilding': GameApiCommand(
        sync_schemas.sync_move_unit_building_schema,
        sync_parser.sync_storage_monster_move,
    ),
    # monster shrine storage
    'ConvertUnitToStorage': GameApiCommand(
        sync_schemas.sync_convert_unit_to_storage_schema,
        sync_parser.sync_convert_monster_to_shrine,
    ),
    # monster shrine storage
    'convertStorageToUnit': GameApiCommand(
        sync_schemas.sync_convert_storage_to_unit_schema,
        sync_parser.sync_convert_monster_from_shrine,
    ),
    # material storage
    'ConvertUnitToItem': GameApiCommand(
        sync_schemas.sync_convert_unit_to_item_schema,
        sync_parser.sync_convert_monster_to_material_storage,
    ),
    # material storage
    'ConvertItemToUnit': GameApiCommand(
        sync_schemas.sync_convert_item_to_unit_schema,
        sync_parser.sync_convert_monster_from_material_storage,
    ),
    'sellInventoryItem': GameApiCommand(
        sync_schemas.sync_sell_inventory_item_schema,
        sync_parser.sync_sell_inventory,
    ),
    'SummonUnit': GameApiCommand(
        data_log_schemas.summon_unit,
        sync_parser.sync_summon_unit,
    ),
    'AssembleUnit_V2': GameApiCommand(
        sync_schemas.sync_monster_from_pieces_schema,
        sync_parser.sync_monster_from_pieces,
    ),
    'AwakenUnit': GameApiCommand(
        sync_schemas.sync_awaken_unit_schema,
        sync_parser.sync_awaken_unit,
    ),
    'SellUnit': GameApiCommand(
        sync_schemas.sync_sell_unit_schema,
        sync_parser.sync_sell_unit,
    ),
    'SacrificeUnit_V3': GameApiCommand(
        sync_schemas.sync_upgrade_unit_v3_schema,
        sync_parser.sync_upgrade_unit,
    ),
    'UpgradeUnit_V3': GameApiCommand(
        sync_schemas.sync_upgrade_unit_v3_schema,
        sync_parser.sync_upgrade_unit,
    ),
    'LockUnit': GameApiCommand(
        sync_schemas.sync_lock_unlock_unit_schema,
        sync_parser.sync_lock_unit,
    ),
    'UnlockUnit': GameApiCommand(
        sync_schemas.sync_lock_unlock_unit_schema,
        sync_parser.sync_unlock_unit,
    ),

}

accepted_api_params = {
    cmd: parser.accepted_commands for cmd, parser in active_log_commands.items()
}
accepted_api_params['__version'] = 1
