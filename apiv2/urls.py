from django.conf.urls import url, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from apiv2 import views

from bestiary.api_urls import router as bestiary_router

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'news', views.ArticleViewSet)

router.registry.extend(bestiary_router.registry)

# TODO: Add a custom API root instead of this auto one with DefaultRouter.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^docs/', include_docs_urls('SWARFARM API Documentation')),  # TODO: Upgrade to next DRF release to fix docs
]
