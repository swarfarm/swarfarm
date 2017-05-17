from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from apiv2 import views

from news.api_urls import router as news_router
from bestiary.api_urls import router as bestiary_router

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)

router.registry.extend(news_router.registry)
router.registry.extend(bestiary_router.registry)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^docs/', include_docs_urls(title='SWARFARM API v2')),
]
