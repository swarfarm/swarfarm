from rest_framework.routers import DefaultRouter
from rest_framework_extensions.routers import ExtendedDefaultRouter

from herders.api_views import *

"""
herders api routes

Personal:
/profile/<username>/
/profile/<username>/storage/
/profile/<username>/buildings/
/profile/<username>/buildings/<id>
/profile/<username>/monsters/
/profile/<username>/monsters/<id>
/profile/<username>/monster-pieces/
/profile/<username>/monster-pieces/<id>
/profile/<username>/runes/
/profile/<username>/runes/<id>
/profile/<username>/rune-crafts/
/profile/<username>/rune-crafts/<id>
/profile/<username>/teams/
/profile/<username>/teams/<id>

Global, for searching and filtering:
/monster-instance/
/monster-instance/<id>
/teams/
/teams/<id>
"""

router = ExtendedDefaultRouter()

profile_routes = router.register(r'profiles', SummonerViewSet, base_name='profiles')
profile_routes.register(
    r'monsters',
    MonsterInstanceViewSet,
    base_name='profile-monsters',
    parents_query_lookups=['owner__user__username'],
)
profile_routes.register(
    r'runes',
    RuneInstanceViewSet,
    base_name='profile-runes',
    parents_query_lookups=['owner__user__username'],
)

router.register(r'monster-instances', MonsterInstanceViewSet, base_name='monster-instances')
router.register(r'rune-instances', RuneInstanceViewSet, base_name='rune-instances')
