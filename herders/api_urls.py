from rest_framework_extensions.routers import ExtendedSimpleRouter

from herders.api_views import *

router = ExtendedSimpleRouter()

(
    router
    .register(r'profiles', SummonerViewSet, base_name='profile')
    .register(
        r'monsters',
        MonsterInstanceViewSet,
        base_name='monsterinstance',
        parents_query_lookups=['owner__user__username']
    )
)
