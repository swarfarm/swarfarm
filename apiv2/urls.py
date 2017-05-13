from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from apiv2 import views

from bestiary.api_urls import router as bestiary_router

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'news', views.ArticleViewSet)

router.registry.extend(bestiary_router.registry)

documented_routes = [
    url(r'^', include(router.urls)),
    url(r'^bestiary/', include(bestiary_router.urls)),
]

urlpatterns = [
    url(r'^docs/', include_docs_urls(title='SWARFARM API v2', patterns=documented_routes)),
] + documented_routes
