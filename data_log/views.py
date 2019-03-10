import json

from rest_framework import viewsets, permissions, versioning, exceptions, parsers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from herders.models import Summoner
from . import game_commands

active_log_commands = {
    'GetBlackMarketList': game_commands.GetBlackMarketList,
    'DoRandomWishItem': game_commands.DoRandomWishItem,
    'SummonUnit': game_commands.SummonUnit,
    'BattleScenarioStart': game_commands.BattleScenarioStart,
    'BattleScenarioResult': game_commands.BattleScenarioResult,
    'BattleDungeonResult': game_commands.BattleDungeonResult,
}

accepted_api_params = {
    cmd: parser.accepted_commands for cmd, parser in active_log_commands.items()
}


class InvalidLogException(exceptions.APIException):
    # An API exception class that formats response into a {'message': xxx, 'reinit': true/false } shape
    status_code = 400
    default_detail = 'Invalid Log Data'
    default_code = 'invalid_log_data'

    def __init__(self, detail=None, code=None, reinit=True):
        message = detail if detail is not None else self.default_detail
        self.code = code if code is not None else self.default_code
        self.detail = {
            'message': exceptions.ErrorDetail(message, self.default_code),
            'reinit': exceptions.ErrorDetail(reinit, self.default_code),
        }


class LogData(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings
    parser_classes = (parsers.JSONParser, parsers.FormParser)

    def create(self, request):
        log_data = request.data.get('data')

        if request.content_type == 'application/x-www-form-urlencoded':
            # log_data will be a string, needs to be parsed as json
            log_data = json.loads(log_data)

        try:
            api_command = log_data['request']['command']
        except (KeyError, TypeError):
            raise InvalidLogException(detail='Invalid log data format')

        if api_command not in active_log_commands:
            raise InvalidLogException('Unsupported game command')

        # Validate log data format
        if not active_log_commands[api_command].validate(log_data):
            raise InvalidLogException(detail='Log data failed validation')

        # Determine the user account providing this log
        if request.user.is_authenticated:
            summoner = request.user.summoner
        else:
            # Attempt to get summoner instance from wizard_id in log data
            wizard_id = log_data['request']['wizard_id']
            summoner = Summoner.objects.filter(com2us_id=wizard_id).first()

        # Parse the log
        active_log_commands[api_command].parse(summoner, log_data)
        return Response({'detail': 'Log OK'})


class AcceptedCommands(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings
    renderer_classes = (JSONRenderer, )

    def list(self, request):
        return Response(accepted_api_params)
