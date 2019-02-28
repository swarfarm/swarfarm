from jsonschema import Draft4Validator

log_schema = {
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'id': 'http://swarfarm.com/schemas/log_data.json',
    'title': 'log_data',
    'type': 'object',
    'properties': {
        'request': {
            'type': 'object',
            'properties': {
                'wizard_id': {'type': 'number'},
                'command': {'type': 'string'},
            },
            'required': ['wizard_id']
        },
        'response': {

        }
    },
    'required': ['request', 'response'],
}

DataLogValidator = Draft4Validator(log_schema)
