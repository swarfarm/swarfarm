from rest_framework.routers import SimpleRouter

# Limited API access (used by UI)
from planner.views import OptimizeTeamViewSet, DungeonViewSet, RosterViewSet

planner = SimpleRouter()
planner.register(r'teams', OptimizeTeamViewSet, base_name='planner-team')
planner.register(r'dungeons', DungeonViewSet, base_name='dungeon')
planner.register(r'rosters', RosterViewSet, base_name='roster')
