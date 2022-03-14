from jsonschema import Draft4Validator

HubUserLoginSchema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/hubuserlogin.json',
    "title": 'HubUserLogin',
    'description': 'Schema for entire HubUserLogin json data',
    'definitions': {
        'rune': {
            'type': 'object',
            'properties': {
                'set_id': {'type': 'number'},
                'class': {
                    'type': 'number',
                    'minimum': 1,
                    'maximum': 16,
                },
                'rank': {'type': 'number'},
                'slot_no': {
                    'type': 'number',
                    'minimum': 1,
                    'maximum': 6,
                },
                'upgrade_curr': {
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 15,
                },
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
                'extra': {'type': 'number'},
            },
            'required': ['set_id', 'class', 'rank', 'slot_no', 'upgrade_curr', 'pri_eff', 'prefix_eff', 'sec_eff', 'sell_value', 'occupied_id', 'base_value', 'upgrade_limit'],
            'additionalProperties': True,
        },
        'monster': {
            'type': 'object',
            'properties': {
                'unit_id': {'type': 'number'},
                'unit_master_id': {'type': 'number'},
                'create_time': {'type': 'string'},
                'unit_level': {
                    'type': 'number',
                    'minimum': 1,
                    'maximum': 40,
                },
                'class': {
                    'type': 'number',
                    'minimum': 1,
                    'maximum': 6,
                },
                'skills': {
                    'type': 'array',
                    'items': {
                        'type': 'array',
                        'items': {'type': 'number'},
                        'minItems': 2,
                        'maxItems': 2,
                    },
                    'minItems': 1,
                    'maxItems': 4,
                },
                'runes': {
                    'oneOf': [
                        {
                            'type': 'array',
                            'items': {'$ref': '#/definitions/rune'},
                            'maxItems': 6,
                        },
                        {
                            'type': 'object',
                            'properties': {
                                '1': {'$ref': '#/definitions/rune'},
                                '2': {'$ref': '#/definitions/rune'},
                                '3': {'$ref': '#/definitions/rune'},
                                '4': {'$ref': '#/definitions/rune'},
                                '5': {'$ref': '#/definitions/rune'},
                                '6': {'$ref': '#/definitions/rune'},
                            }
                        }
                    ]
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
                'required': ['craft_type', 'craft_type_id', 'craft_item_id'],
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
        'unit_storage_list': {
            'type': 'array',
            'items': {
                'quantity': {'type': 'number'},
                'unit_master_id': {'type': 'number'},
                'class': {'type': 'number'},
            },
            'required': ['unit_master_id', 'quantity']
        },
        'runes': {
            'type': 'array',
            'items': {'$ref': '#/definitions/rune'},
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
            'items': {'$ref': '#/definitions/monster'},
        },
        'world_arena_rune_equip_list': {
            'type': 'array',
            'items': {
                'rune_id': {'type': 'number'},
                'occupied_id': {'type': 'number'},
            }
        },
        'world_arena_artifact_equip_list': {
            'type': 'array',
            'items': {
                'artifact_id': {'type': 'number'},
                'occupied_id': {'type': 'number'},
            }
        },
        'wizard_id': {'type': 'number'},
        'command': {'type': 'string'},
        'server_id': {'type': 'number'},
    },
    'required': [
        'building_list',
        'rune_craft_item_list',
        'deco_list',
        'inventory_info',
        'runes',
        'world_arena_rune_equip_list',
        'world_arena_artifact_equip_list',
        'wizard_info',
        'unit_list'
    ],
}

VisitFriendSchema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/hubuserlogin.json',
    "title": 'HubUserLogin',
    'description': 'Schema for entire VisitFriend json data',
    'definitions': HubUserLoginSchema['definitions'],
    'type': 'object',
    'properties': {
        'friend': {
            'type': 'object',
            'properties': {
                'unit_list': {
                    'type': 'array',
                    'items': {'$ref': '#/definitions/monster'},
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
            },
            'required': ['unit_list', 'building_list', 'deco_list',],
        },
    },
    'required': ['friend'],
}

HubUserLoginValidator = Draft4Validator(HubUserLoginSchema)
VisitFriendValidator = Draft4Validator(VisitFriendSchema)
