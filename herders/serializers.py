from django.contrib.auth.models import User

from rest_framework import serializers

from herders.models import Summoner


class SummonerSerializer(serializers.HyperlinkedModelSerializer):
    profile_name = serializers.CharField(source='summoner.summoner_name', allow_blank=True)
    server = serializers.ChoiceField(source='summoner.server', choices=Summoner.SERVER_CHOICES)
    public = serializers.BooleanField(source='summoner.public')

    class Meta:
        model = User
        fields = ('url', 'username', 'profile_name', 'server', 'public')
        extra_kwargs = {
            'url': {
                'lookup_field': 'username',
                'view_name': 'apiv2:profiles-detail',
            },
        }
