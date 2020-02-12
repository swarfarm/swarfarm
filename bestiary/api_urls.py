from rest_framework import routers

from bestiary import api_views as viewsets

router = routers.DefaultRouter()
router.register(r'monsters', viewsets.MonsterViewSet, base_name='bestiary/monsters')
router.register(r'monster-sources', viewsets.MonsterSourceViewSet, base_name='bestiary/monster-sources')
router.register(r'skills', viewsets.MonsterSkillViewSet, base_name='bestiary/skills')
router.register(r'skill-effects', viewsets.MonsterSkillEffectViewSet, base_name='bestiary/skill-effects')
router.register(r'leader-skills', viewsets.MonsterLeaderSkillViewSet, base_name='bestiary/leader-skills')
router.register(r'homunculus-skills', viewsets.HomunculusSkillViewSet, base_name='bestiary/homunculus-skills')
router.register(r'items', viewsets.GameItemViewSet, base_name='bestiary/items')
router.register(r'fusions', viewsets.FusionViewSet, base_name='bestiary/fusions')
router.register(r'buildings', viewsets.BuildingViewSet, base_name='bestiary/buildings')
router.register(r'dungeons', viewsets.DungeonViewSet, base_name='bestiary/dungeons')
router.register(r'levels', viewsets.LevelViewSet, base_name='bestiary/levels')
