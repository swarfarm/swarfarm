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

sync_sell_inventory_item_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_sell_inventory_item.json',
    'title': 'sync_sell_inventory_item',
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
                'item_info': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'item_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_monster_from_pieces_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_monster_from_pieces.json',
    'title': 'sync_monster_from_pieces',
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
                'unit_info': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'item_list',
                'unit_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_awaken_unit_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_awaken_unit.json',
    'title': 'sync_awaken_unit',
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
                'unit_info': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_sell_unit_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_sell_unit.json',
    'title': 'sync_sell_unit',
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
                'unit_info': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_upgrade_unit_v3_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_upgrade_unit_v3.json',
    'title': 'sync_upgrade_unit_v3',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'source_unit_list': {'type': 'array'},
            },
            'required': ['wizard_id', 'command', 'source_unit_list'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'unit_info': {'type': 'object'},
                'inventory_item_list': {'type': 'array'},
                'unit_storage_list': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_info',
                'inventory_item_list',
                'unit_storage_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_lock_unlock_unit_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_lock_unlock_unit.json',
    'title': 'sync_lock_unlock_unit',
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
                'unit_id': {'type': 'number'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'unit_id',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_upgrade_rune_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_upgrade_rune.json',
    'title': 'sync_upgrade_rune',
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
                'rune': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'rune',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_sell_rune_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_sell_rune.json',
    'title': 'sync_sell_rune',
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
                'runes': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'runes',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_grind_enchant_rune_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_grind_enchant_rune.json',
    'title': 'sync_grind_enchant_rune',
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
                'rune': {'type': 'object'},
                'rune_craft_item': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'rune',
                'rune_craft_item',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_reapp_rune_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_reapp_rune.json',
    'title': 'sync_reapp_rune',
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
                'rune': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'rune',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_equip_rune_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_equip_rune.json',
    'title': 'sync_equip_rune',
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
                'removed_rune': {'type': ['null', 'object']},
                'rune_id': {'type': 'number'},
                'unit_info': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'rune_id',
                'unit_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_change_runes_in_rune_management_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_change_runes_in_rune_management.json',
    'title': 'sync_change_runes_in_rune_management',
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
                'equip_rune_id_list': {'type': 'array'},
                'unequip_rune_id_list': {'type': 'array'},
                'unit_info': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'equip_rune_id_list',
                'unequip_rune_id_list',
                'unit_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_unequip_rune_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_unequip_rune.json',
    'title': 'sync_unequip_rune',
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
                'rune': {'type': 'object'},
                'unit_info': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'rune',
                'unit_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_upgrade_artifact_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_upgrade_artifact.json',
    'title': 'sync_upgrade_artifact',
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
                'artifact': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'artifact',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_sell_artifacts_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_sell_artifacts.json',
    'title': 'sync_sell_artifacts',
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
                'artifact_ids': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'artifact_ids',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_artifact_pre_enchant_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_artifact_pre_enchant.json',
    'title': 'sync_artifact_pre_enchant',
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
                'inventory_info': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'inventory_info',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_artifact_post_enchant_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_artifact_post_enchant.json',
    'title': 'sync_artifact_post_enchant',
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
                'artifact': {'type': 'object'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'artifact',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_change_artifact_assignment_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_change_artifact_assignment.json',
    'title': 'sync_change_artifact_assignment',
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
                'updated_artifacts': {'type': 'array'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'updated_artifacts',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}

sync_reward_daily_quest_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_reward_daily_quest.json',
    'title': 'sync_reward_daily_quest',
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

sync_receive_mail_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_receive_mail.json',
    'title': 'sync_receive_mail',
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
                'rune_list': {'type': ['array', 'null']},
                'unit_list': {'type': ['array', 'null']},
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

sync_receive_guild_siege_reward_crate_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/sync_receive_guild_siege_reward_crate.json',
    'title': 'sync_receive_guild_siege_reward_crate',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
                'crate_index': {'type': 'number'},
            },
            'required': ['wizard_id', 'command'],
        },
        'response': {
            'type': 'object',
            'properties': {
                'tzone': {'type': 'string'},
                'tvalue': {'type': 'number'},
                'crate_list': {'type': 'array', 'null'},
                'command': {'type': 'string'},
            },
            'required': [
                'tzone',
                'tvalue',
                'crate_list',
                'command',
            ]
        }
    },
    'required': ['request', 'response'],
}
