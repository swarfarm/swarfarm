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
    url(r'bestiary/(?P<pk>[0-9]+)/chart/$', views.bestary_stat_charts, name='bestiary_stat_chart'),
]
