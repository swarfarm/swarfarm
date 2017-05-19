from rest_framework import viewsets, filters

from herders.serializers import *
from herders.pagination import *
from herders.permissions import *


class SummonerViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().select_related('summoner')
    serializer_class = SummonerSerializer
    pagination_class = SummonerPagination
    permission_classes = [IsStaffOrOwner]
    lookup_field = 'username'

    def get_queryset(self):
        queryset = super(SummonerViewSet, self).get_queryset()
        if self.request.user.is_superuser:
            return queryset
        else:
            return queryset.filter(summoner__public=True)
