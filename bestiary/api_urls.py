from rest_framework import routers

from bestiary.api_views import *

router = routers.DefaultRouter()
router.register(r'monsters', MonsterViewSet, base_name='bestiary/monsters')
router.register(r'skills', MonsterSkillViewSet, base_name='bestiary/skills')
router.register(r'homunculus-skill', HomunculusSkillViewSet, base_name='bestiary/homunculus-skill')
router.register(r'skill-effect', MonsterSkillEffectViewSet, base_name='bestiary/skill-effect')
