from django.contrib.auth.models import User
from rest_framework import serializers

from herders.models import Summoner


class UserSerializer(serializers.HyperlinkedModelSerializer):
    summoner_name = serializers.CharField(source='summoner.summoner_name', allow_blank=True)
    server = serializers.ChoiceField(source='summoner.server', choices=Summoner.SERVER_CHOICES)
    public = serializers.BooleanField(source='summoner.public')
    timezone = serializers.CharField(source='summoner.timezone', allow_blank=True)

    class Meta:
        model = User
        fields = ('url', 'username', 'password', 'email', 'is_staff', 'summoner_name', 'server', 'public', 'timezone')
        extra_kwargs = {
            'password': {'write_only': True},
            'is_staff': {'read_only': True},
            'url': {'lookup_field': 'username'},
        }

    def create(self, validated_data):
        summoner_data = validated_data.pop('summoner', None)
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        self.create_or_update_summoner(user, summoner_data)
        user.save()

        return user

    def update(self, instance, validated_data):
        summoner_data = validated_data.pop('summoner', None)
        self.create_or_update_summoner(instance, summoner_data)
        return super(UserSerializer, self).update(instance, validated_data)

    def create_or_update_summoner(self, user, summoner_data):
        summoner, created = Summoner.objects.get_or_create(user=user, defaults=summoner_data)

        if not created and summoner_data is not None:
            super(UserSerializer, self).update(summoner, summoner_data)
