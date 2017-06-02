from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from herders.routers import NestedStorageRouter
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

router = DefaultRouter()
router.register(r'profiles', SummonerViewSet, base_name='profiles')
router.register(r'monster-instances', MonsterInstanceViewSet, base_name='monster-instances')
router.register(r'rune-instances', RuneInstanceViewSet, base_name='rune-instances')

profile_router = NestedDefaultRouter(router, r'profiles', lookup='user')
profile_router.register(r'monsters', MonsterInstanceViewSet, base_name='profile/monsters')
profile_router.register(r'monster-pieces', MonsterPieceViewSet, base_name='profile/monster-pieces')
profile_router.register(r'runes', RuneInstanceViewSet, base_name='profile/runes')
profile_router.register(r'rune-crafts', RuneCraftInstanceViewSet, base_name='profile/rune-crafts')
profile_router.register(r'buildings', BuildingViewSet, base_name='profile/buildings')
profile_router.register(r'team-groups', TeamGroupViewSet, base_name='profile/team-groups')
profile_router.register(r'teams', TeamViewSet, base_name='profile/teams')

storage_router = NestedStorageRouter(router, r'profiles', lookup='user')
storage_router.register(r'storage', StorageViewSet, base_name='profile/storage')
