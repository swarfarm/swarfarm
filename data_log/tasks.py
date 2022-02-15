from datetime import timedelta, datetime

from celery import shared_task
from django.db import transaction
from django.db.models import Q, Count
from django.utils import timezone

from bestiary.models import Monster
from .models import DungeonLog, RiftRaidLog, WorldBossLog, StatisticsReport
from .reports.generate import generate_dungeon_log_reports, generate_magic_box_crafting_reports, generate_rift_raid_reports, generate_rift_dungeon_reports, generate_shop_refresh_reports, generate_summon_reports, generate_wish_reports, \
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
def _generate_monster_statistic_report(start_date, monster_pk, server, is_rta, min_box_6stars, profile_pks):
    with transaction.atomic():
        profiles = Summoner.objects.filter(pk__in=profile_pks)\
            .prefetch_related('monsterinstance')\
            .select_related('monsterinstance__defaultbuild', 'monsterinstance__rtabuild')
        monster = Monster.objects.get(pk=monster_pk)
        report = {}
        sr = StatisticsReport.objects.create(
            start_date=datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S").date(),
            monster=monster,
            server=server,
            is_rta=is_rta,
            min_box_6stars=min_box_6stars,
            report=report
        )
        monsterinstances = sr.monsterinstances(profiles, filter_by_date=False)

        sr.generate_report(monsterinstances)

        print(f"Report #{sr.pk} for {sr.monster} generated from {start_date} to {timezone.now().date()}")


@shared_task
def generate_statistics_reports():
    # 180d earlier
    start_date = (timezone.now() - timedelta(days=180)).date()
    servers = [None] + list(dict(Summoner.SERVER_CHOICES).keys())
    monsters = Monster.objects.filter(awaken_level__in=[Monster.AWAKEN_LEVEL_AWAKENED, Monster.AWAKEN_LEVEL_SECOND], obtainable=True)
    is_rta_options = [False, True]
    min_box_6stars_list = [0, 50, 100, 200]

    profiles = Summoner.objects\
        .filter(consent_report__isnull=False, last_update__date__gte=start_date)\
        .prefetch_related('monsterinstance')\
        .select_related('monsterinstance__defaultbuild', 'monsterinstance__rtabuild')

    for server in servers:
        profiles_f = profiles
        if server:
            profiles_f = profiles_f.filter(server=server)
        for min_box_6stars in min_box_6stars_list:
            if min_box_6stars:
                profiles_f = profiles_f.annotate(stars6=Count('monsterinstance__stars')).filter(stars6__gte=min_box_6stars).distinct()
            for monster in monsters: 
                for is_rta in is_rta_options:
                    _generate_monster_statistic_report.delay(start_date, monster.pk, server, is_rta, min_box_6stars, list(profiles_f.values_list('pk', flat=True)))
                    print(start_date, monster, server, is_rta, min_box_6stars, profiles_f.count())
