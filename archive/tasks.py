from datetime import timedelta

from celery import shared_task
from django.utils import timezone

from archive.helpers import archive_world_boss_logs, archive_wish_logs, archive_dungeon_logs, archive_rift_dungeon_logs, \
    archive_raid_dungeon_logs, archive_magic_box_craft_logs, archive_shop_refresh_logs, archive_summon_logs, archive_craft_rune_logs, \
    archive_full_logs, archive_reports


@shared_task
def archive_old_logs(date_to=None):
    WEEKS_TO = 2
    if date_to is None:
        date_to = timezone.now() - timedelta(weeks=WEEKS_TO)
    if not timezone.is_aware(date_to):
        date_to = timezone.make_aware(date_to)

    archive_world_boss_logs(date_to)
    archive_wish_logs(date_to)
    archive_dungeon_logs(date_to)
    archive_rift_dungeon_logs(date_to)
    archive_raid_dungeon_logs(date_to)
    archive_magic_box_craft_logs(date_to)
    archive_shop_refresh_logs(date_to)
    archive_summon_logs(date_to)
    archive_craft_rune_logs(date_to)
    archive_full_logs(date_to)

    archive_reports(date_to)
