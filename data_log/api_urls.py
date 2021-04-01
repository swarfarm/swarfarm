from rest_framework import routers

from . import views

app_name = 'log_data'

router = routers.SimpleRouter()
router.register(r'data_logs', views.LogData, basename='log-upload')
urlpatterns = router.urls
