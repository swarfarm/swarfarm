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
        sync_parser.sync_secret_dungeon_result,
    )
}

accepted_api_params = {
    cmd: parser.accepted_commands for cmd, parser in active_log_commands.items()
}
accepted_api_params['__version'] = 1
