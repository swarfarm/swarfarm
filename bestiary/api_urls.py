from rest_framework import routers

from bestiary import api_views as viewsets

router = routers.DefaultRouter()
router.register(r'monsters', viewsets.MonsterViewSet, basename='bestiary/monsters')
router.register(r'monster-sources', viewsets.MonsterSourceViewSet, basename='bestiary/monster-sources')
router.register(r'skills', viewsets.MonsterSkillViewSet, basename='bestiary/skills')
router.register(r'skill-effects', viewsets.MonsterSkillEffectViewSet, basename='bestiary/skill-effects')
router.register(r'leader-skills', viewsets.MonsterLeaderSkillViewSet, basename='bestiary/leader-skills')
router.register(r'homunculus-skills', viewsets.HomunculusSkillViewSet, basename='bestiary/homunculus-skills')
router.register(r'items', viewsets.GameItemViewSet, basename='bestiary/items')
router.register(r'fusions', viewsets.FusionViewSet, basename='bestiary/fusions')
router.register(r'buildings', viewsets.BuildingViewSet, basename='bestiary/buildings')
router.register(r'dungeons', viewsets.DungeonViewSet, basename='bestiary/dungeons')
router.register(r'levels', viewsets.LevelViewSet, basename='bestiary/levels')
