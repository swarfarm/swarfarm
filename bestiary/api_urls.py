from rest_framework import routers

from bestiary.api_views import *

router = routers.DefaultRouter()
router.register(r'monster', MonsterViewSet, base_name='bestiary/monster')
router.register(r'monster-source', MonsterSourceViewSet, base_name='bestiary/monster-source')
router.register(r'skill', MonsterSkillViewSet, base_name='bestiary/skill')
router.register(r'skill-effect', MonsterSkillEffectViewSet, base_name='bestiary/skill-effect')
router.register(r'leader-skill', MonsterLeaderSkillViewSet, base_name='bestiary/leader-skill')
router.register(r'homunculus-skill', HomunculusSkillViewSet, base_name='bestiary/homunculus-skill')
router.register(r'craft-material', CraftMaterialViewSet, base_name='bestiary/craft-material')
