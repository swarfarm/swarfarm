from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from planner.views import OptimizeTeamViewSet, DungeonViewSet, RosterViewSet, PlannerViewSet

planner = DefaultRouter()
planner.register(r'planner', PlannerViewSet, basename='planner')
planner_user = NestedDefaultRouter(planner, r'planner', lookup='user')
planner_user.register(r'teams', OptimizeTeamViewSet, basename='planner-team')
planner_user.register(r'roster', RosterViewSet, basename='roster')
planner_user.register(r'dungeons', DungeonViewSet, basename='dungeon')
