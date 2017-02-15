
HubUserLoginSchema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/hubuserlogin.json',
    "title": 'HubUserLogin',
    'description': 'Schema for entire HubUserLogin json data',
    'definitions': {
        'rune': {
            'type': 'object',
            'properties': {
                # Required for importing
                'set_id': {'type': 'number'},
                'class': {'type': 'number'},
                'rank': {'type': 'number'},
                'slot_no': {'type': 'number'},
                'upgrade_curr': {'type': 'number'},
                'pri_eff': {
                    'type': 'array',
                    'items': {'type': 'number'},
                    'minItems': 2,
                    'maxItems': 2,
                },
                'prefix_eff': {
                    'type': 'array',
                    'items': {'type': 'number'},
                    'maxItems': 2,
                },
                'sec_eff': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {'type': 'number'},
                        'minItems': 4,
                        'maxItems': 4,
                    }
                },
                'sell_value': {'type': 'number'},
                'occupied_id': {'type': 'number'},
                'wizard_id': {'type': 'number'},
            },
            'required': ['set_id', 'class', 'rank', 'slot_no', 'upgrade_curr', 'pri_eff', 'prefix_eff', 'sec_eff', 'sell_value', 'occupied_id', 'base_value', 'upgrade_limit'],
            'additionalProperties': True,
        },
        'monster': {
            'type': 'object',
            'properties': {
                # Required for importing
                'unit_id': {'type': 'number'},
                'unit_master_id': {'type': 'number'},
                'create_time': {'type': 'string'},
                'unit_level': {'type': 'number'},
                'class': {'type': 'number'},
                'skills': {
                    'type': 'array',
                    'items': {'type': 'number'},
                    'minItems': 1,
                    'maxItems': 4,
                },
                'runes': {
                    'type': 'array',
                    'items': {'type': {'$ref': '#/definitions/rune'}},
                    'maxItems': 6,
                },
                'building_id': {'type': 'number'},
                'wizard_id': {'type': 'number'},
                'homunculus': {'type': 'number'},
                'homunculus_name': {'type': 'string'},
            },
            'required': ['unit_id', 'unit_master_id', 'create_time', 'unit_level', 'class', 'skills', 'runes', 'building_id', 'wizard_id', 'homunculus', 'homunculus_name'],
            'additionalProperties': True,
        }
    },
    'type': 'object',
    'properties': {
        'unit_lock_list': {
            'type': 'array',
            'items': {'type': 'number'},
        },
        'building_list': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'building_id': {'type': 'number'},
                    'building_master_id': {'type': 'number'},
                },
                'required': ['building_id', 'building_master_id'],
            }
        },
        'rune_craft_item_list': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'sell_value': {'type': 'number'},
                    'craft_type_id': {'type': 'number'},
                    'craft_item_id': {'type': 'number'},
                    'craft_type': {'type': 'number'},
                },
                'required': ['craft_type', 'craft_type_id', 'craft_item_id', 'craft_type'],
            }
        },
        'deco_list': {
            'type': 'array',
            'items': {
                'type': 'object',
                'properties': {
                    'deco_id': {'type': 'number'},
                    'level': {'type': 'number'},
                    'master_id': {'type': 'number'},
                },
                'required': ['master_id', 'level', 'deco_id']
            }
        },
        'inventory_info': {
            'type': 'array',
            'items': {
                'item_master_type': {'type': 'number'},
                'item_quantity': {'type': 'number'},
                'item_master_id': {'type': 'number'},
                'wizard_id': {'type': 'number'},
            },
            'required': ['item_master_type', 'item_quantity', 'item_master_id']
        },
        'runes': {
            'type': 'array',
            'items': {'type': {'$ref': '#/definitions/rune'}},
        },
        'wizard_info': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
            },
            'required': ['wizard_id'],
        },
        'unit_list': {
            'type': 'array',
            'items': {'type': {'$ref': '#/definitions/monster'}},
        },
        'wizard_id': {'type': 'number'},
        'command': {'type': 'string'},
    },
    'required': ['unit_lock_list', 'building_list', 'rune_craft_item_list', 'deco_list', 'inventory_info', 'runes', 'wizard_info', 'unit_list', 'wizard_id', 'command'],
}
