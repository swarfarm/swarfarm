from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'monster', views.MonsterViewSet)
router.register(r'monster/skill', views.MonsterSkillViewSet)
router.register(r'monster/skill/leader', views.MonsterLeaderSkillViewSet)
router.register(r'monster/skill/effect', views.MonsterSkillEffectViewSet)
router.register(r'monster/source', views.MonsterSourceViewSet)

urlpatterns = [
    # REST framework stuff
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
]
