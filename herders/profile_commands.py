import json

from jsonschema import Draft4Validator

from bestiary.parse.dungeons import dispatch_dungeon_wave_parse
from bestiary.models import Monster
from data_log.game_commands import GameApiCommand
from .models import MonsterShrineStorage
from . import schemas
from .tasks import com2us_data_import, swex_sync_monster_shrine
from .profile_parser import validate_sw_json, default_import_options


def sync_profile(summoner, log_data):
    schema_errors, validation_errors = validate_sw_json(log_data['response'], summoner)
    if schema_errors or validation_errors:
        return

    import_options = summoner.preferences.get('import_options', default_import_options)
    com2us_data_import.delay(log_data['response'], summoner.pk, import_options)


def sync_monster_shrine(summoner, log_data):
    swex_sync_monster_shrine.delay(log_data['response'], summoner.pk)

# Map to in-game commands and generate list of accepted API params
active_log_commands = {
    'HubUserLogin': GameApiCommand(
        schemas.sync_hub_user_login_schema,
        sync_profile,
    ),
    'getUnitStorageList': GameApiCommand(
        schemas.sync_get_unit_storage_list_schema,
        sync_monster_shrine,
    )
}

accepted_api_params = {
    cmd: parser.accepted_commands for cmd, parser in active_log_commands.items()
}
accepted_api_params['__version'] = 1
