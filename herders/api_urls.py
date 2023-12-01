from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from herders.api_views import *
from herders.routers import NestedStorageRouter

"""
herders api routes

Personal:
/profile/<username>/
/profile/<username>/storage/
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
router.register(r'profiles/upload', ProfileJsonUpload, basename='profile/upload')
router.register(r'profiles/sync', SyncData, basename='sync-profile')
router.register(r'profiles/accepted-commands', SyncAcceptedCommands, basename='sync-accepted-commands')
router.register(r'profiles', SummonerViewSet, basename='profiles')

profile_router = NestedDefaultRouter(router, r'profiles', lookup='user')
profile_router.register(r'monsters', MonsterInstanceViewSet, basename='profile/monsters')
profile_router.register(r'monster-pieces', MonsterPieceViewSet, basename='profile/monster-pieces')
profile_router.register(r'runes', RuneInstanceViewSet, basename='profile/runes')
profile_router.register(r'artifacts', ArtifactInstanceViewSet, basename='profile/artifacts')
profile_router.register(r'rune-builds', RuneBuildViewSet, basename='profile/rune-builds')
profile_router.register(r'rune-crafts', RuneCraftInstanceViewSet, basename='profile/rune-crafts')
profile_router.register(r'team-groups', TeamGroupViewSet, basename='profile/team-groups')
profile_router.register(r'teams', TeamViewSet, basename='profile/teams')
profile_router.register(r'upload', ProfileJsonUpload, basename='profile/upload_legacy')
profile_router.register(r'storage', StorageViewSet, basename='profile/storage')
profile_router.register(r'monster-shrine', MonsterShrineStorageViewSet, basename='profile/monster-shrine')
