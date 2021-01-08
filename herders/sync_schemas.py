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