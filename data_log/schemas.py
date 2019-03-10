# JSON Schemas for all logged game API commands, used to validate shape of data submitted by users and to generate a
# list of required keys for each API command for logging clients.

get_black_market_list = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/get_black_market_list.json',
    'title': 'get_black_market_list',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'cash_used': {'type': ['null', 'number']},
            },
            'required': ['wizard_id', 'command'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'market_info': {'type': 'object'},
                'market_list': {'type': 'array'},
            },
            'required': [
                'tzone',
                'tvalue',
                'market_info',
                'market_list',
            ]
        }
    },
    'required': ['request', 'response'],
}

do_random_wish_item = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/do_random_wish_item.json',
    'title': 'do_random_wish_item',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
            },
            'required': ['wizard_id', 'command'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'wish_info': {'type': 'object'},
                'rune': {'type': ['null', 'object']},
                'unit_info': {'type': ['null', 'object']},
            },
            'required': [
                'tzone',
                'tvalue',
                'wish_info',
            ]
        }
    },
    'required': ['request', 'response'],
}

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

battle_scenario_start = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_scenario_start.json',
    'title': 'battle_scenario_start',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'region_id': {'type': 'number'},
                'stage_no': {'type': 'number'},
                'difficulty': {'type': 'number'},
            },
            'required': [
                'wizard_id',
                'command',
                'region_id',
                'stage_no',
                'difficulty',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'battle_key': {'type': 'number'},
            },
            'required': [
                'battle_key',
            ]
        }
    },
    'required': ['request', 'response'],
}

battle_scenario_result = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_scenario_result.json',
    'title': 'battle_scenario_result',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'battle_key': {'type': 'number'},
                'win_lose': {'type': 'number'},
                'clear_time': {'type': 'number'},
            },
            'required': [
                'wizard_id',
                'command',
                'battle_key',
                'win_lose',
                'clear_time',
            ],
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

battle_dungeon_result = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_dungeon_result.json',
    'title': 'battle_dungeon_result',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'dungeon_id': {'type': 'number'},
                'stage_id': {'type': 'number'},
                'win_lose': {'type': 'number'},
                'clear_time': {'type': 'number'},
            },
            'required': [
                'wizard_id',
                'command',
                'dungeon_id',
                'stage_id',
                'win_lose',
                'clear_time',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'reward': {'type': 'object'},
                'instance_info': {'type': ['null', 'object']},
            },
            'required': [
                'tzone',
                'tvalue',
                'reward',
            ]
        }
    },
    'required': ['request', 'response'],
}



# Old static list of accepted API params here for posterity
# accepted_api_params = {
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