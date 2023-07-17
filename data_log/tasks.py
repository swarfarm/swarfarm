from datetime import timedelta

from celery import shared_task
from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone

from bestiary.models import Monster
from .models import DungeonLog, RiftRaidLog, WorldBossLog, StatisticsReport
from .reports.generate import generate_dungeon_log_reports, generate_magic_box_crafting_reports, generate_rift_raid_reports, generate_rift_dungeon_reports, \
    generate_shop_refresh_reports, generate_summon_reports, generate_wish_reports, \
    generate_world_boss_dungeon_reports, generate_rune_crafting_reports
from herders.models import Summoner


@shared_task
def generate_all_reports():
    generate_dungeon_log_reports()
    generate_rift_raid_reports()
    generate_rift_dungeon_reports()
    generate_world_boss_dungeon_reports()
    generate_shop_refresh_reports()
    generate_magic_box_crafting_reports()
    generate_wish_reports()
    generate_summon_reports()
    generate_rune_crafting_reports()


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


@shared_task
def _generate_monster_statistic_report(start_date, monster_id, server, is_rta, min_box_6stars, profile_pks):
    with transaction.atomic():
        monster = Monster.objects.get(pk=monster_id)
        profiles = Summoner.objects.filter(pk__in=profile_pks)\
            .prefetch_related('monsterinstance')\
            .select_related('monsterinstance__defaultbuild', 'monsterinstance__rtabuild')
        report = {}
        sr = StatisticsReport.objects.create(
            start_date=start_date,
            monster=monster,
            server=server,
            is_rta=is_rta,
            min_box_6stars=min_box_6stars,
            report=report
        )
        monsterinstances = sr.monsterinstances(profiles, filter_by_date=False, server=server)
        sr.generate_report(monsterinstances)


@shared_task
def generate_statistics_reports(server_idx=0, is_rta=False, min_box_6stars=0, days_timespan=180):
    start_date = (timezone.now() - timedelta(days=days_timespan)).date()
    servers = [None] + list(dict(Summoner.SERVER_CHOICES).keys())
    monsters = Monster.objects.filter(awaken_level__in=[Monster.AWAKEN_LEVEL_AWAKENED, Monster.AWAKEN_LEVEL_SECOND], obtainable=True)

    profiles = Summoner.objects\
        .filter(consent_report=True, last_update__date__gte=start_date)\
        .prefetch_related('monsterinstance')\
        .select_related('monsterinstance__defaultbuild', 'monsterinstance__rtabuild')

    server = servers[server_idx]
    if server:
        profiles = profiles.filter(server=server)
    if min_box_6stars:
        profiles = profiles.filter(monsterinstance__stars=6, monsterinstance__level=40).distinct().annotate(stars6=Count('monsterinstance')).filter(stars6__gte=min_box_6stars).distinct()
    
    for monster in monsters:
        _generate_monster_statistic_report.delay(start_date.strftime("%Y-%m-%d"), monster.pk, server, is_rta, min_box_6stars, list(profiles.values_list('pk', flat=True)))

    ## debugging
    # c = monsters.count()
    # for idm, monster in enumerate(monsters):
    #   _generate_monster_statistic_report(start_date.strftime("%Y-%m-%d"), monster.pk, server, is_rta, min_box_6stars, list(profiles.values_list('pk', flat=True)))
    #   print("Elapsed time:", round(time.time() - start_time, 2), "Done:", idm + 1, '/', c, '(', round((idm + 1) / c * 100, 2), '%)')
