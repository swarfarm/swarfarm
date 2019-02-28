from rest_framework import routers

from . import views

app_name = 'log_data'

router = routers.SimpleRouter()
router.register(r'log/upload', views.LogData, base_name='log-upload')
router.register(r'log/accepted_commands', views.AcceptedCommands, base_name='log-accepted-commands')
urlpatterns = router.urls
