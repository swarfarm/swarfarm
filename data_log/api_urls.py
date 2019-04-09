from rest_framework import routers

from . import views, api_views

app_name = 'log_data'

router = routers.SimpleRouter()
router.register(r'data_logs', views.LogData, base_name='log-upload')
router.register(r'data_logs/dungeons', api_views.DungeonLogViewSet)
urlpatterns = router.urls
