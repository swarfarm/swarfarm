import json

from rest_framework import viewsets, permissions, versioning, exceptions, parsers
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from herders.models import Summoner
from . import game_commands

active_log_commands = {
    'SummonUnit': game_commands.SummonUnitCommand,
    'BattleScenarioResult': game_commands.BattleScenarioResultCommand,
}

accepted_api_params = {
    cmd: parser.accepted_commands for cmd, parser in active_log_commands.items()
}


class LogData(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny, )
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings
    parser_classes = (parsers.JSONParser, parsers.FormParser)

    def create(self, request):
        log_data = request.data.get('data')

        if request.content_type == 'application/x-www-form-urlencoded':
            # log_data key will be a string, needs to be parsed as json
            log_data = json.loads(log_data)

        try:
            api_command = log_data['request']['command']
        except (KeyError, TypeError):
            raise exceptions.ParseError(detail='Invalid log data format')

        if api_command not in active_log_commands:
            raise exceptions.ParseError(detail='Unsupported Game Command')

        # Validate log data format
        if not active_log_commands[api_command].validate(log_data):
            raise exceptions.ParseError(detail='Invalid log data format')

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
