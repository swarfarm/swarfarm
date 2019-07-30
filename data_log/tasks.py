from celery import shared_task

from .reports.generate import generate_dungeon_log_reports, generate_rift_raid_reports, generate_rift_dungeon_reports, \
    generate_world_boss_dungeon_reports


@shared_task
def generate_all_reports():
    generate_dungeon_log_reports()
    generate_rift_raid_reports()
    generate_rift_dungeon_reports()
    generate_world_boss_dungeon_reports()
