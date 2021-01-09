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
    # crafting runes too
    'BuyShopItem': GameApiCommand(
        data_log_schemas.buy_shop_item,
        sync_parser.sync_buy_item,
    ),
}

accepted_api_params = {
    cmd: parser.accepted_commands for cmd, parser in active_log_commands.items()
}
accepted_api_params['__version'] = 1
