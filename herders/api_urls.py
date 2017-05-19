from rest_framework import routers

from herders.api_views import *

router = routers.DefaultRouter()

router.register(r'profiles', SummonerViewSet, base_name='profiles')
