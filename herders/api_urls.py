from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from herders.api_views import *
from herders.routers import NestedStorageRouter

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
/profile/<username>/artifacts/
/profile/<username>/artifacts/<id>
/profile/<username>/rune-builds/
/profile/<username>/rune-builds/id
/profile/<username>/rune-crafts/
/profile/<username>/rune-crafts/<id>
/profile/<username>/teams/
/profile/<username>/teams/<id>
"""

router = DefaultRouter()
router.register(r'profiles/upload', ProfileJsonUpload, base_name='profile/upload')
router.register(r'profiles/sync', SyncData, base_name='sync-profile')
router.register(r'profiles/accepted-commands', SyncAcceptedCommands, base_name='sync-accepted-commands')
router.register(r'profiles', SummonerViewSet, base_name='profiles')

profile_router = NestedDefaultRouter(router, r'profiles', lookup='user')
profile_router.register(r'monsters', MonsterInstanceViewSet, base_name='profile/monsters')
profile_router.register(r'monster-pieces', MonsterPieceViewSet, base_name='profile/monster-pieces')
profile_router.register(r'runes', RuneInstanceViewSet, base_name='profile/runes')
profile_router.register(r'artifacts', ArtifactInstanceViewSet, base_name='profile/artifacts')
profile_router.register(r'rune-builds', RuneBuildViewSet, base_name='profile/rune-builds')
profile_router.register(r'rune-crafts', RuneCraftInstanceViewSet, base_name='profile/rune-crafts')
profile_router.register(r'buildings', BuildingViewSet, base_name='profile/buildings')
profile_router.register(r'team-groups', TeamGroupViewSet, base_name='profile/team-groups')
profile_router.register(r'teams', TeamViewSet, base_name='profile/teams')
profile_router.register(r'upload', ProfileJsonUpload, base_name='profile/upload_legacy')
profile_router.register(r'storage', StorageViewSet, base_name='profile/storage')
profile_router.register(r'monster-shrine', MonsterShrineStorageViewSet, base_name='profile/monster-shrine')
