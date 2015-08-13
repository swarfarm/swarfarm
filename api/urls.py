from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'bestiary', views.MonsterViewSet)
router.register(r'skill', views.MonsterSkillViewSet)
router.register(r'skill_effect', views.MonsterSkillEffectViewSet)
router.register(r'leader_skill', views.MonsterLeaderSkillViewSet)
router.register(r'source', views.MonsterSourceViewSet)

router.register(r'summoner', views.SummonerViewSet)
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
