# JSON Schemas for all logged game API commands, used to validate shape of data submitted by users and to generate a
# list of required keys for each API command for logging clients.

# TODO: expand depth of schema properties to cover for all of what is used in code, not just what is required
# for accepted API params

sync_hub_user_login_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_hub_user_login.json',
    'title': 'sync_hub_user_login',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'command': {'type': 'string'},
            },
            'required': [],
        },
        'response': {
            'type': 'object',
            'properties': {
                'command': {'type': 'string'},
            },
            'required': ['command'],
        },
    },
    'required': ['response'],
}

sync_get_unit_storage_list_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_get_unit_storage_list.json',
    'title': 'sync_get_unit_storage_list',
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
                'unit_storage_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_storage_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_battle_instance_result_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_sync_battle_instance_result.json',
    'title': 'sync_battle_instance_result',
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
                'item_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'item_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_pick_guild_maze_battle_clear_reward_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_pick_guild_maze_battle_clear_reward.json',
    'title': 'sync_pick_guild_maze_battle_clear_reward',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'battle_key': {'type': 'number'},
                'pick_set_id': {'type': 'number'},
            },
            'required': ['wizard_id', 'command', 'battle_key', 'pick_set_id'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'pick_rune_list': {'type': 'array'},
                'pick_changestone_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'pick_rune_list',
                'pick_changestone_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_battle_trial_tower_result_v2_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_battle_trial_tower_result_v2.json',
    'title': 'sync_battle_trial_tower_result_v2',
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
                'reward': {'type': 'object'},
                'changed_item_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'reward',
                'changed_item_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_buy_guild_black_market_item_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_buy_guild_black_market_item.json',
    'title': 'sync_buy_guild_black_market_item',
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
                'item_list': {'type': ['array', 'null']},
                'rune_list': {'type': ['array', 'null']},
                'runecraft_list': {'type': ['array', 'null']},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_buy_black_market_item_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_buy_black_market_item.json',
    'title': 'sync_buy_black_market_item',
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
                'runes': {'type': ['array', 'null']},
                'unit_info': {'type': ['object', 'null']},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_move_unit_building_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_move_unit_building.json',
    'title': 'sync_move_unit_building',
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
                'unit_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_convert_unit_to_storage_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_convert_unit_to_storage.json',
    'title': 'sync_convert_unit_to_storage',
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
                'remove_unit_id_list': {'type': 'array'},
                'unit_storage_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'remove_unit_id_list',
                'unit_storage_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_convert_storage_to_unit_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_convert_storage_to_unit.json',
    'title': 'sync_convert_storage_to_unit',
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
                'add_unit_list': {'type': 'array'},
                'unit_storage_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'add_unit_list',
                'unit_storage_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_convert_unit_to_item_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_convert_unit_to_item.json',
    'title': 'sync_convert_unit_to_item',
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
                'remove_unit_id_list': {'type': 'array'},
                'inventory_item_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'remove_unit_id_list',
                'inventory_item_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_convert_item_to_unit_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_convert_item_to_unit.json',
    'title': 'sync_convert_item_to_unit',
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
                'add_unit_list': {'type': 'array'},
                'inventory_item_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'add_unit_list',
                'inventory_item_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}
