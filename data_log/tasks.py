from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from .models import DungeonLog, RiftRaidLog, WorldBossLog
from .reports.generate import generate_dungeon_log_reports, generate_rift_raid_reports, generate_rift_dungeon_reports, \
    generate_world_boss_dungeon_reports


@shared_task
def generate_all_reports():
    generate_dungeon_log_reports()
    generate_rift_raid_reports()
    generate_rift_dungeon_reports()
    generate_world_boss_dungeon_reports()


can_be_incomplete_logs = [
    DungeonLog,
    RiftRaidLog,
    WorldBossLog,
]


@shared_task
def clean_incomplete_logs():
    # Delete all incomplete logs that do not have success specified after 1 day
    days_old = timedelta(days=1)
    result = {}

    for m in can_be_incomplete_logs:
        del_count = m.objects.filter(success__isnull=True, timestamp__lte=timezone.now() - days_old)
        result[m.__name__] = del_count

    return result
