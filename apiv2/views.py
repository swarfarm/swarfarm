from refreshtoken.models import RefreshToken
from herders.serializers import FullUserSerializer


# JWT response to include user data
def jwt_response_payload_handler(token, user=None, request=None):
    payload = {
        'token': token,
        'user': FullUserSerializer(user, context={'request': request}).data
    }

    app = 'swarfarm'

    try:
        refresh_token = user.refresh_tokens.get(app=app).key
    except RefreshToken.DoesNotExist:
        # Create it
        refresh_token = user.refresh_tokens.create(app=app).key

    payload['refresh_token'] = refresh_token
    return payload
