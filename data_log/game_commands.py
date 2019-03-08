import json
from jsonschema import Draft4Validator

from .models import SummonLog, DungeonLog
from . import schemas


class GameApiCommand:
    def __init__(self, schema, parse_fn):
        self.validator = Draft4Validator(schema)
        self.accepted_commands = {
            key: schema['properties'][key]['required'] for key in schema['required']
        }
        self.parser = parse_fn

    def parse(self, *args, **kwargs):
        return self.parser(*args, **kwargs)

    def validate(self, log_data):
        return self.validator.is_valid(log_data)


SummonUnitCommand = GameApiCommand(schemas.summon_unit, SummonLog.parse_summon_log)
BattleScenarioResultCommand = GameApiCommand(schemas.battle_scenario_result, DungeonLog.parse_scenario_result)


# Utility functions
def import_swex_full_log(path, search_commands):
    req = None
    capture = False
    command = None
    outfile_count = 1

    with open(path, 'r') as f:
        for line in f:
            if line.startswith('API Command:'):
                command = line[13:line.find(' -')]
                capture = command in search_commands

            if line.startswith('Request:'):
                req = json.loads(f.readline())

            if line.startswith('Response:'):
                resp = json.loads(f.readline())

                if capture and command:
                    with open(f'{outfile_count}_{command}.json', 'w') as o:
                        json.dump({
                            'data': {
                                'request': req,
                                'response': resp,
                            }
                        }, o, indent=2)
                    command = None
                    capture = False
                    outfile_count += 1
