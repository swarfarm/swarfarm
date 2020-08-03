import json

from jsonschema import Draft4Validator

from bestiary.parse.dungeons import dispatch_dungeon_wave_parse
from . import models
from . import schemas


class GameApiCommand:
    def __init__(self, schema, parse_fns):
        self.validator = Draft4Validator(schema)
        self.accepted_commands = {
            key: schema['properties'][key]['properties'].keys() for key in schema['required']
        }
        if not isinstance(parse_fns, list):
            parse_fns = [parse_fns]
        self.parsers = parse_fns

    def parse(self, *args, **kwargs):
        for fn in self.parsers:
            fn(*args, **kwargs)

    def validate(self, log_data):
        return self.validator.is_valid(log_data)


# Arbitrator function for BuyShopItem which could be a rune or a magic box
def buy_shop_item(summoner, log_data):
    item_id = log_data['request']['item_id']

    if item_id in models.CraftRuneLog.PARSE_IDS:
        models.CraftRuneLog.parse_buy_shop_item(summoner, log_data)
    elif item_id in models.MagicBoxCraft.PARSE_IDS:
        models.MagicBoxCraft.parse_buy_shop_item(summoner, log_data)


# Map to in-game commands and generate list of accepted API params
active_log_commands = {
    'GetBlackMarketList': GameApiCommand(
        schemas.get_black_market_list,
        models.ShopRefreshLog.parse_shop_refresh
    ),
    'DoRandomWishItem': GameApiCommand(
        schemas.do_random_wish_item,
        models.WishLog.parse_wish_log
    ),
    'BuyShopItem': GameApiCommand(
        schemas.buy_shop_item,
        buy_shop_item
    ),
    'SummonUnit': GameApiCommand(
        schemas.summon_unit,
        models.SummonLog.parse_summon_log
    ),
    'ConfirmSummonChoice': GameApiCommand(
        schemas.select_blessing_unit,
        models.SummonLog.parse_blessing_choice
    ),
    'BattleScenarioStart': GameApiCommand(
        schemas.battle_scenario_start,
        [models.DungeonLog.parse_scenario_start, dispatch_dungeon_wave_parse]
    ),
    'BattleScenarioResult': GameApiCommand(
        schemas.battle_scenario_result,
        models.DungeonLog.parse_scenario_result
    ),
    'BattleDungeonStart': GameApiCommand(
        schemas.battle_dungeon_start,
        dispatch_dungeon_wave_parse
    ),
    'BattleDungeonResult_V2': GameApiCommand(
        schemas.battle_dungeon_result_v2,
        models.DungeonLog.parse_dungeon_result_v2
    ),
    'BattleRiftDungeonResult': GameApiCommand(
        schemas.battle_rift_dungeon_result,
        models.RiftDungeonLog.parse_rift_dungeon_result
    ),
    'BattleWorldBossStart': GameApiCommand(
        schemas.battle_world_boss_start,
        models.WorldBossLog.parse_world_boss_start
    ),
    'BattleWorldBossResult': GameApiCommand(
        schemas.battle_world_boss_result,
        models.WorldBossLog.parse_world_boss_result
    ),
    'BattleRiftOfWorldsRaidStart': GameApiCommand(
        schemas.battle_rift_of_worlds_raid_start,
        models.RiftRaidLog.parse_rift_raid_start
    ),
    'BattleRiftOfWorldsRaidResult': GameApiCommand(
        schemas.battle_rift_of_worlds_raid_result,
        models.RiftRaidLog.parse_rift_raid_result
    ),
    'BattleDimensionHoleDungeonResult_v2': GameApiCommand(
        schemas.battle_dimension_hole_result_v2,
        models.DungeonLog.parse_dimension_hole_result_v2
    )
}

accepted_api_params = {
    cmd: parser.accepted_commands for cmd, parser in active_log_commands.items()
}
accepted_api_params['__version'] = 8


# Utility functions
def import_swex_full_log(path, search_commands):
    req = None
    capture = False
    command = None
    outfile_count = 1

    with open(path, 'r') as f:
        for line in f:
            if line.startswith('API Command:'):
                command = line[13:line.find(' -')]
                capture = command in search_commands

            if line.startswith('Request:'):
                req = json.loads(f.readline())

            if line.startswith('Response:'):
                resp = json.loads(f.readline())

                if capture and command:
                    with open(f'{outfile_count}_{command}.json', 'w') as o:
                        json.dump({
                            'data': {
                                'request': req,
                                'response': resp,
                            }
                        }, o, indent=2)
                    command = None
                    capture = False
                    outfile_count += 1
