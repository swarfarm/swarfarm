from django.conf.urls import url, include
from rest_framework import routers
from apiv2 import views

from news.api_urls import router as news_router
from bestiary.api_urls import router as bestiary_router
from herders.api_urls import router as herders_router, profile_router, team_router

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

router.registry.extend(news_router.registry)
router.registry.extend(bestiary_router.registry)
router.registry.extend(herders_router.registry)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(profile_router.urls)),
    url(r'^', include(team_router.urls)),
]
