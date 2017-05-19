from rest_framework import routers

from bestiary.api_views import *

router = routers.DefaultRouter()
router.register(r'monsters', MonsterViewSet, base_name='bestiary/monsters')
router.register(r'monster-sources', MonsterSourceViewSet, base_name='bestiary/monster-sources')
router.register(r'skills', MonsterSkillViewSet, base_name='bestiary/skills')
router.register(r'skill-effects', MonsterSkillEffectViewSet, base_name='bestiary/skill-effects')
router.register(r'homunculus-skills', HomunculusSkillViewSet, base_name='bestiary/homunculus-skills')
router.register(r'craft-materials', CraftMaterialViewSet, base_name='bestiary/craft-materials')
router.register(r'fusions', FusionViewSet, base_name='bestiary/fusions')
router.register(r'buildings', BuildingViewSet, base_name='bestiary/buildings')
