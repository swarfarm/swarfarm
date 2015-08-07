from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'bestiary/monster', views.MonsterViewSet)
router.register(r'bestiary/monster/skill', views.MonsterSkillViewSet)
router.register(r'bestiary/monster/skill/leader', views.MonsterLeaderSkillViewSet)
router.register(r'bestiary/monster/skill/effect', views.MonsterSkillEffectViewSet)
router.register(r'bestiary/monster/source', views.MonsterSourceViewSet)

router.register(r'summoner', views.SummonerViewSet)
#router.register(r'monster', views.MonsterInstanceViewSet)
router.register(r'runes', views.RuneInstanceViewSet)
router.register(r'group', views.TeamGroupViewSet)
router.register(r'team', views.TeamViewSet)

urlpatterns = [
    # REST framework stuff
    url(r'^', include(router.urls)),
    url(r'^profile/(?P<profile_name>[a-zA-Z0-9_@.]+)/monster/$', views.MonsterInstanceViewSet.as_view({'get': 'list'})),
    url(r'^profile/(?P<profile_name>[a-zA-Z0-9_@.]+)/monster/(?P<pk>[0-9a-f]{32})/$', views.MonsterInstanceViewSet.as_view({'get': 'retrieve'})),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
]
