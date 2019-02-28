from rest_framework import viewsets, permissions, versioning, exceptions
from rest_framework.response import Response

from herders.models import Summoner

from .log_schema import DataLogValidator
from .log_parse import accepted_api_params, log_parse_dispatcher

# Notes for future:
# Get summoner instance with API key, pass to log parse functions. Fall back to wizard id lookup. None if no matches.
# Get information on what game data for starting a secret dungeon looks like


class LogData(viewsets.ViewSet):
    permission_classes = (permissions.AllowAny,)
    versioning_class = versioning.QueryParameterVersioning  # Ignore default of namespaced based versioning and use default version defined in settings

    def create(self, request):
        log_data = request.data.get('data')
        if not DataLogValidator.is_valid(log_data):
            raise exceptions.ParseError(detail='Invalid log data format')

        api_command = log_data['request']['command']
        if api_command not in accepted_api_params:
            raise exceptions.APIException(detail='Unsupported Game Command')

        # Determine the user account providing this log
        if request.user.is_authenticated:
            summoner = request.user.summoner
        else:
            # Attempt to get summoner instance from wizard_id in log data
            wizard_id = log_data['request']['wizard_id']
            summoner = Summoner.objects.filter(com2us_id=wizard_id).first()

        # Parse the log
        log_parse_dispatcher[api_command](summoner, log_data)
        return Response({'detail': 'Log OK'})
