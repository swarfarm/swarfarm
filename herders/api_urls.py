from rest_framework.routers import DefaultRouter

from herders.api_views import *

router = DefaultRouter()
router.register(r'profiles', SummonerViewSet, base_name='profile')
router.register(r'monster-instances', MonsterInstanceViewSet, base_name='monster-instance')
router.register(r'rune-instances', RuneInstanceViewSet, base_name='rune-instance')
