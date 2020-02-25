# JSON Schemas for all logged game API commands, used to validate shape of data submitted by users and to generate a
# list of required keys for each API command for logging clients.

# TODO: expand depth of schema properties to cover for all of what is used in code, not just what is required
# for accepted API params

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

buy_shop_item = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/buy_shop_item.json',
    'title': 'buy_shop_item',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'item_id': {'type': 'number'},
            },
            'required': ['wizard_id', 'command', 'item_id'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'reward': {'type': ['null', 'object']},
                'view_item_list': {'type': ['null', 'array']},
            },
            'required': [
                'tzone',
                'tvalue',
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
                'summon_choices': {'type': 'array'},
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

select_blessing_unit = {
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
                'rid': {'type': 'number'},
            },
            'required': ['wizard_id', 'command', 'rid'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'unit_list': {'type': 'array'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_list',
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
                'opp_unit_list': {'type': 'array'},
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
            },
            'required': [
                'battle_key',
                'tzone',
                'tvalue',
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
                'reward': {'type': 'object'},
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

battle_dungeon_start = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_dungeon_start.json',
    'title': 'battle_dungeon_start',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'dungeon_id': {'type': 'number'},
                'stage_id': {'type': 'number'},
            },
            'required': [
                'wizard_id',
                'command',
                'dungeon_id',
                'stage_id',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'dungeon_unit_list': {'type': 'array'},
            },
            'required': [
                'tzone',
                'tvalue',
                'dungeon_unit_list',
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

battle_rift_dungeon_result = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_rift_dungeon_result.json',
    'title': 'battle_rift_dungeon_result',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'dungeon_id': {'type': 'number'},
                'battle_result': {'type': 'number'},
                'clear_time': {'type': 'number'},
            },
            'required': [
                'wizard_id',
                'command',
                'dungeon_id',
                'battle_result',
                'clear_time',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'total_damage': {'type': 'number'},
                'rift_dungeon_box_id': {'type': 'number'},
                'item_list': {'type': ['null', 'array']},
            },
            'required': [
                'tzone',
                'tvalue',
                'rift_dungeon_box_id',
                'total_damage',
            ]
        }
    },
    'required': ['request', 'response'],
}

battle_world_boss_start = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_world_boss_start.json',
    'title': 'battle_world_boss_start',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'worldboss_id': {'type': 'number'},
                'unit_id_list': {'type': 'array'},
            },
            'required': [
                'wizard_id',
                'command',
                'worldboss_id',
                'unit_id_list',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'battle_key': {'type': 'number'},
                'worldboss_battle_result': {'type': 'object'},
            },
            'required': [
                'tzone',
                'tvalue',
                'battle_key',
                'worldboss_battle_result',
            ]
        }
    },
    'required': ['request', 'response'],
}

battle_world_boss_result = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_world_boss_start.json',
    'title': 'battle_world_boss_start',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'battle_key': {'type': 'number'},
            },
            'required': [
                'wizard_id',
                'command',
                'battle_key',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'reward_info': {'type': ['null', 'object']},
                'reward': {'type': ['null', 'object']},
            },
            'required': [
                'tzone',
                'tvalue',
                'reward_info',
                'reward',
            ]
        }
    },
    'required': ['request', 'response'],
}

battle_rift_of_worlds_raid_start = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_rift_of_worlds_raid_start.json',
    'title': 'battle_rift_of_worlds_raid_start',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'battle_key': {'type': 'number'},
            },
            'required': [
                'wizard_id',
                'command',
                'battle_key',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'battle_info': {'type': 'object'},
            },
            'required': [
                'tzone',
                'tvalue',
                'battle_info',
            ]
        }
    },
    'required': ['request', 'response'],
}

battle_rift_of_worlds_raid_result = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_rift_of_worlds_raid_start.json',
    'title': 'battle_rift_of_worlds_raid_start',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'battle_key': {'type': 'number'},
                'clear_time': {'type': 'number'},
                'win_lose': {},
                'user_status_list': {},
            },
            'required': [
                'wizard_id',
                'command',
                'battle_key',
                'clear_time',
            ],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'battle_reward_list': {'type': 'array'},
            },
            'required': [
                'tzone',
                'tvalue',
                'battle_reward_list',
            ]
        }
    },
    'required': ['request', 'response'],
}

battle_dimension_hole_result = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/battle_dimension_hole_result.json',
    'title': 'battle_dimension_hole_result',
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
            'required': [
                'wizard_id',
                'command',
                'win_lose',
                'clear_time',
            ]
        },
        'response': {
            'type': 'object',
            'properties': {
                'dungeon_id': {'type': 'number'},
                'difficulty': {'type': 'number'},
                'reward': {'type': 'object'},
                'practice_mode': {'type': 'number'},
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
            },
            'required': [
                'dungeon_id',
                'difficulty',
                'reward',
                'practice_mode',
                'tzone',
                'tvalue',
            ]
        }
    },
    'required': ['request', 'response'],
}
