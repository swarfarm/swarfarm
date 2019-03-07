import json

from rest_framework import viewsets, permissions, versioning, exceptions, parsers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from herders.models import Summoner
from .models import SummonLog, DungeonLog
from .log_schema import DataLogValidator


accepted_api_params = {
    'SummonUnit': {
        'request': [
            'wizard_id',
            'command',
            'mode',
        ],
        'response': [
            'tzone',
            'tvalue',
            'unit_list',
            'item_list',
        ],
    },
    # 'DoRandomWishItem': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #     ],
    #     'response': [
    #         'tzone',
    #         'tvalue',
    #         'wish_info',
    #         'unit_info',
    #         'rune',
    #     ]
    # },
    # 'BattleDungeonResult': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #         'dungeon_id',
    #         'stage_id',
    #         'clear_time',
    #         'win_lose',
    #     ],
    #     'response': [
    #         'tzone',
    #         'tvalue',
    #         'unit_list',
    #         'reward',
    #         'instance_info',
    #     ]
    # },
    'BattleScenarioResult': {
        'request': [
            'wizard_id',
            'command',
            'win_lose',
            'clear_time',
        ],
        'response': [
            'tzone',
            'tvalue',
            'scenario_info',
            'reward',
        ]
    },
    # 'BattleWorldBossStart': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #     ],
    #     'response': [
    #         'tzone',
    #         'tvalue',
    #         'battle_key',
    #         'worldboss_battle_result',
    #         'reward_info',
    #     ]
    # },
    # 'BattleWorldBossResult': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #         'battle_key',
    #     ],
    #     'response': [
    #         'reward',
    #     ]
    # },
    # 'BattleRiftDungeonResult': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #         'battle_result',
    #         'dungeon_id'
    #     ],
    #     'response': [
    #         'tvalue',
    #         'tzone',
    #         'item_list',
    #         'rift_dungeon_box_id',
    #         'total_damage',
    #     ]
    # },
    # 'BattleRiftOfWorldsRaidStart': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #         'battle_key',
    #     ],
    #     'response': [
    #         'tzone',
    #         'tvalue',
    #         'battle_info',
    #     ]
    # },
    # 'BattleRiftOfWorldsRaidResult': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #         'battle_key',
    #         'clear_time',
    #         'win_lose',
    #         'user_status_list',
    #     ],
    #     'response': [
    #         'tzone',
    #         'tvalue',
    #         'battle_reward_list',
    #         'reward',
    #     ]
    # },
    # 'BuyShopItem': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #         'item_id',
    #     ],
    #     'response': [
    #         'tzone',
    #         'tvalue',
    #         'reward',
    #         'view_item_list',
    #     ]
    # },
    # 'GetBlackMarketList': {
    #     'request': [
    #         'wizard_id',
    #         'command',
    #     ],
    #     'response': [
    #         'tzone',
    #         'tvalue',
    #         'market_info',
    #         'market_list',
    #     ],
    # },
}

log_parse_dispatcher = {
    'SummonUnit': SummonLog.parse_summon_log,
    # 'DoRandomWishItem': parse_do_random_wish_item,
    # 'BattleDungeonResult': parse_battle_dungeon_result,
    'BattleScenarioResult': DungeonLog.parse_scenario_result,
    # 'BattleWorldBossStart': parse_battle_worldboss_start,
    # 'BattleWorldBossResult': parse_battle_worldboss_result,
    # 'BattleRiftDungeonResult': parse_battle_rift_dungeon_result,
    # 'BattleRiftOfWorldsRaidStart': parse_battle_rift_of_worlds_raid_start,
    # 'BattleRiftOfWorldsRaidResult': parse_battle_rift_of_worlds_raid_end,
    # 'BuyShopItem': parse_buy_shop_item,
    # 'GetBlackMarketList': parse_get_black_market_list,
}


class LogData(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings
    parser_classes = (parsers.JSONParser, parsers.FormParser)

    def create(self, request):
        log_data = request.data.get('data')

        if request.content_type == 'application/x-www-form-urlencoded':
            # log_data key will be a string, needs to be parsed as json
            log_data = json.loads(log_data)

        if not DataLogValidator.is_valid(log_data):
            raise exceptions.ParseError(detail='Invalid log data format')

        api_command = log_data['request']['command']
        if api_command not in accepted_api_params:
            raise exceptions.ParseError(detail='Unsupported Game Command')

        # Determine the user account providing this log
        if request.user.is_authenticated:
            summoner = request.user.summoner
        else:
            # Attempt to get summoner instance from wizard_id in log data
            wizard_id = log_data['request']['wizard_id']
            summoner = Summoner.objects.filter(com2us_id=wizard_id).first()

        # Parse the log
        log_parse_dispatcher[api_command](summoner, log_data)
        return Response({'detail': 'Log OK'})


class AcceptedCommands(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings
    renderer_classes = (JSONRenderer, )

    def list(self, request):
        return Response(accepted_api_params)
