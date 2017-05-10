from rest_framework import routers

from bestiary.api_views import *

router = routers.SimpleRouter()
router.register(r'monsters', MonsterViewSet, base_name='bestiary/monsters')
router.register(r'skills', MonsterSkillViewSet)
