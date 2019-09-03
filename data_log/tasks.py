from datetime import timedelta

from celery import shared_task
from django.db.models import Q
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


@shared_task
def clean_incomplete_logs():
    # Delete all logs older than 1 day which have only had a start event captured, and no result event
    log_is_old = Q(timestamp__lte=timezone.now() - timedelta(days=1))
    result = {
        DungeonLog.__name__: DungeonLog.objects.filter(log_is_old, success__isnull=True).delete(),
        RiftRaidLog.__name__: RiftRaidLog.objects.filter(log_is_old, success__isnull=True).delete(),
        WorldBossLog.__name__: WorldBossLog.objects.filter(log_is_old, grade__isnull=True).delete(),
    }

    return result
