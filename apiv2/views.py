from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
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


@login_required
def generate_basic_auth_token(request, *args, **kwargs):
    # Token value is the PK, so regenerating a token requires deleting and adding it rather than just updating it.
    Token.objects.filter(user=request.user).delete()
    token = Token.objects.create(user=request.user)

    return JsonResponse({'token': token.key})
