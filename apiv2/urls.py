from django.conf.urls import url, include
from rest_framework import routers
from rest_framework_swagger.views import get_swagger_view

from news.api_urls import router as news_router
from bestiary.api_urls import router as bestiary_router
from herders.api_urls import router as herders_router, profile_router
from data_log.api_urls import router as data_log_router

app_name = 'apiv2'

router = routers.DefaultRouter()
router.registry.extend(news_router.registry)
router.registry.extend(bestiary_router.registry)
router.registry.extend(herders_router.registry)
router.registry.extend(data_log_router.registry)

api_urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^', include(profile_router.urls)),
    url(r'^', include(data_log_router.urls)),
]

schema_view = get_swagger_view(
    title='SWARFARM API v2',
    url='/api/v2/',
    patterns=api_urlpatterns
)

urlpatterns = api_urlpatterns + [
    url(r'^docs/$', schema_view),
]
