import json

from django.core import serializers
from django.http import HttpResponse

from herders.models import Monster

# Create your views here.
def monster(request, monster_id):
    data = serializers.serialize('json', [Monster.objects.get(pk=monster_id), ])

    return HttpResponse(
        data,
        content_type="application/json"
    )
