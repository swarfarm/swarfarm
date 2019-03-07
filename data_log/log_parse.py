import json


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
