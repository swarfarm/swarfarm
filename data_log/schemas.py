summon_unit = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/summon_schema.json',
    'title': 'summon_schema',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'mode': {'type': 'number'},
            },
            'required': ['wizard_id', 'command', 'mode'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'unit_list': {'type': 'array'},
                'item_list': {'type': 'array'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_list',
                'item_list',
            ]
        }
    },
    'required': ['request', 'response'],
}

battle_scenario_result = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/summon_schema.json',
    'title': 'summon_schema',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'win_lose': {'type': 'number'},
                'clear_time': {'type': 'number'},
            },
            'required': ['wizard_id', 'command', 'win_lose', 'clear_time'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'scenario_info': {'type': 'object'},
                'reward': {'type': 'object'},
            },
            'required': [
                'tzone',
                'tvalue',
                'scenario_info',
                'reward',
            ]
        }
    },
    'required': ['request', 'response'],
}


# Old static list of accepted API params here for posterity
# accepted_api_params = {
#     'SummonUnit': {
#         'request': [
#             'wizard_id',
#             'command',
#             'mode',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'unit_list',
#             'item_list',
#         ],
#     },
#     'DoRandomWishItem': {
#         'request': [
#             'wizard_id',
#             'command',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'wish_info',
#             'unit_info',
#             'rune',
#         ]
#     },
#     'BattleDungeonResult': {
#         'request': [
#             'wizard_id',
#             'command',
#             'dungeon_id',
#             'stage_id',
#             'clear_time',
#             'win_lose',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'unit_list',
#             'reward',
#             'instance_info',
#         ]
#     },
#     'BattleScenarioResult': {
#         'request': [
#             'wizard_id',
#             'command',
#             'win_lose',
#             'clear_time',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'scenario_info',
#             'reward',
#         ]
#     },
#     'BattleWorldBossStart': {
#         'request': [
#             'wizard_id',
#             'command',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'battle_key',
#             'worldboss_battle_result',
#             'reward_info',
#         ]
#     },
#     'BattleWorldBossResult': {
#         'request': [
#             'wizard_id',
#             'command',
#             'battle_key',
#         ],
#         'response': [
#             'reward',
#         ]
#     },
#     'BattleRiftDungeonResult': {
#         'request': [
#             'wizard_id',
#             'command',
#             'battle_result',
#             'dungeon_id'
#         ],
#         'response': [
#             'tvalue',
#             'tzone',
#             'item_list',
#             'rift_dungeon_box_id',
#             'total_damage',
#         ]
#     },
#     'BattleRiftOfWorldsRaidStart': {
#         'request': [
#             'wizard_id',
#             'command',
#             'battle_key',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'battle_info',
#         ]
#     },
#     'BattleRiftOfWorldsRaidResult': {
#         'request': [
#             'wizard_id',
#             'command',
#             'battle_key',
#             'clear_time',
#             'win_lose',
#             'user_status_list',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'battle_reward_list',
#             'reward',
#         ]
#     },
#     'BuyShopItem': {
#         'request': [
#             'wizard_id',
#             'command',
#             'item_id',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'reward',
#             'view_item_list',
#         ]
#     },
#     'GetBlackMarketList': {
#         'request': [
#             'wizard_id',
#             'command',
#         ],
#         'response': [
#             'tzone',
#             'tvalue',
#             'market_info',
#             'market_list',
#         ],
#     },
# }