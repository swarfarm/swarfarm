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
router.register(r'instance', views.MonsterInstanceViewSet)
router.register(r'runes', views.RuneInstanceViewSet)
router.register(r'group', views.TeamGroupViewSet)
router.register(r'team', views.TeamViewSet)

urlpatterns = [
    # REST framework stuff
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Custom API stuff
    url(r'^runes/stats_by_slot/(?P<slot>[0-9])/$', views.get_rune_stats_by_slot, name='rune_stat_by_slot'),
    url(r'^runes/stats_by_craft/(?P<craft_type>[0-9])/$', views.get_craft_stats_by_type, name='craft_stats_by_type'),
    url(r'^messages/$', views.get_user_messages, name='user_messages'),
]
