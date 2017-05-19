from django.contrib.auth.models import User

from rest_framework import serializers
from rest_framework.reverse import reverse

from herders.models import Summoner, MonsterInstance


class SummonerSerializer(serializers.ModelSerializer):
    profile_name = serializers.CharField(source='summoner.summoner_name', allow_blank=True)
    server = serializers.ChoiceField(source='summoner.server', choices=Summoner.SERVER_CHOICES)
    public = serializers.BooleanField(source='summoner.public')

    class Meta:
        model = User
        fields = ('url', 'username', 'profile_name', 'server', 'public')
        extra_kwargs = {
            'url': {
                'lookup_field': 'username',
                'view_name': 'apiv2:profile-detail',
            },
        }


class MonsterInstanceSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    monster = serializers.HyperlinkedRelatedField(view_name='apiv2:bestiary/monsters-detail', read_only=True)

    class Meta:
        model = MonsterInstance
        fields = [
            'url', 'pk', 'com2us_id', 'created', 'monster',
            'stars', 'level', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level',
            'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes',
        ]

    def get_url(self, instance):
        return reverse('apiv2:monsterinstance-detail', args=['porksmash', str(instance.pk)], request=self.context['request'])