from rest_framework import routers

from . import views

app_name = 'log_data'

router = routers.SimpleRouter()
router.register(r'data_logs', views.LogData, base_name='log-upload')
urlpatterns = router.urls
