from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'bestiary', views.MonsterViewSet)
router.register(r'skill', views.MonsterSkillViewSet)
router.register(r'skill_effect', views.MonsterSkillEffectViewSet)
router.register(r'leader_skill', views.MonsterLeaderSkillViewSet)
router.register(r'source', views.MonsterSourceViewSet)

urlpatterns = [
    # REST framework stuff
    url(r'^', include(router.urls)),

    # Custom API stuff
    url(r'^nightbot/', include([
        url('^(?P<profile_name>[a-zA-Z0-9_@.]+)/monster/(?P<monster_name>[a-zA-Z0-9_@.]+)/$', views.nightbot_monsters, name='nightbot_monsters'),
    ])),
    url(r'^runes/stats_by_slot/(?P<slot>[0-9])/$', views.get_rune_stats_by_slot, name='rune_stat_by_slot'),
    url(r'^runes/stats_by_craft/(?P<craft_type>[0-9])/$', views.get_craft_stats_by_type, name='craft_stats_by_type'),
    url(r'bestiary/(?P<pk>[0-9]+)/chart/$', views.bestary_stat_charts, name='bestiary_stat_chart'),
    url(r'^messages/$', views.get_user_messages, name='user_messages'),
]
