from datetime import timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Min, Max, Avg, Sum
from django_pivot.histogram import histogram

from bestiary.models import Dungeon, Level
from .models import Report, LevelReport, SummonLog, DungeonLog, ItemDrop, MonsterDrop, MonsterPieceDrop, RuneDrop, RuneCraftDrop, DungeonSecretDungeonDrop
from .util import floor_to_nearest, ceil_to_nearest, replace_value_with_choice


def _records_to_report(qs, report_timespan=timedelta(weeks=2), minimum_count=2500):
    if qs.filter(timestamp__gte=timezone.now() - report_timespan).count() < minimum_count:
        # Return latest minimum_count logs, ignoring report timespan
        return qs[:minimum_count]
    else:
        return qs.filter(timestamp__gte=timezone.now() - report_timespan)


def get_report_summary(drops):
    summary = {}

    for drop_type, qs in drops.items():
        if drop_type == ItemDrop.RELATED_NAME:
            # Item drops are counted individually and contain quantity information
            summary_data = list(
                qs.values(
                    'item',
                    'item__name',
                    'item__icon'
                ).annotate(
                    count=Count('item'),
                    min=Min('quantity'),
                    max=Max('quantity'),
                    avg=Avg('quantity')
                ).order_by('-count')
            )
        elif drop_type == MonsterDrop.RELATED_NAME:
            # Monster drops are counted by stars
            summary_data = list(qs.values('grade').annotate(count=Count('pk')))
        else:
            # Count only
            summary_data = qs.aggregate(count=Count('pk'))

        summary[drop_type] = summary_data

    return summary


def get_item_report(qs, total_runs):
    results = list(
        qs.values(
            'item',
            'item__name',
            'item__icon'
        ).annotate(
            count=Count('item'),
            min=Min('quantity'),
            max=Max('quantity'),
            avg=Avg('quantity'),
            sum=Sum('quantity'),
        ).order_by('-count')
    )

    for result in results:
        result['drop_chance'] = float(result['count']) / total_runs
        result['avg_per_run'] = float(result['sum']) / total_runs

    return results


def get_monster_report(qs, total_runs):
    return "monster report"


def get_monster_piece_report(qs, total_runs):
    return "monster piece report"


def get_rune_report(qs, total_runs):
    results = dict()
    results['summary'] = {
        'stars': list(qs.values('stars').annotate(count=Count('pk')).order_by('-count')),
        'type': replace_value_with_choice(
            list(qs.values('type').annotate(count=Count('pk')).order_by('-count')),
            'type',
            qs.model.TYPE_CHOICES,
        ),
        'quality': replace_value_with_choice(
            list(qs.values('quality').annotate(count=Count('pk')).order_by('-count')),
            'quality',
            qs.model.QUALITY_CHOICES,
        ),
        'slot': list(qs.values('slot').annotate(count=Count('pk')).order_by('-count')),
    }

    # Main stat distribution

    # Innate stat distribution

    # Substat distribution

    # Maximum efficiency by quality
    results['max_efficiency'] = histogram(qs, 'max_efficiency', range(0, 100, 5), slice_on='quality')

    # Sell value by quality
    min_value, max_value = qs.aggregate(Min('value'), Max('value')).values()
    min_value = int(floor_to_nearest(min_value, 1000))
    max_value = int(ceil_to_nearest(max_value, 1000))
    results['value'] = histogram(qs, 'value', range(min_value, max_value, 1000), slice_on='quality')

    return results


def get_rune_craft_report(qs, total_runs):
    return "rune craft report"


def get_secret_dungeon_report(qs, total_runs):
    return "secret dungeon report"


DROP_TYPES = {
    ItemDrop.RELATED_NAME: get_item_report,
    MonsterDrop.RELATED_NAME: get_monster_report,
    MonsterPieceDrop.RELATED_NAME: get_monster_piece_report,
    RuneDrop.RELATED_NAME: get_rune_report,
    RuneCraftDrop.RELATED_NAME: get_rune_craft_report,
    DungeonSecretDungeonDrop.RELATED_NAME: get_secret_dungeon_report,
}


def get_drop_querysets(qs):
    drop_querysets = {}

    for drop_type in DROP_TYPES.keys():
        # Get querysets for each possible drop type
        if hasattr(qs.model, drop_type):
            drop_model = getattr(qs.model, drop_type).field.model
            drop_querysets[drop_type] = drop_model.objects.filter(log__in=qs)

    return drop_querysets


def generate_scenario_reports():
    content_type = ContentType.objects.get_for_model(DungeonLog)

    for level in Level.objects.filter(dungeon__category=Dungeon.CATEGORY_SCENARIO):
        records = _records_to_report(DungeonLog.objects.filter(level=level), minimum_count=5)

        if records.count() > 0:
            report_data = {}

            # Get querysets for each possible drop type
            drops = get_drop_querysets(records)
            report_data['summary'] = get_report_summary(drops)

            for key, qs in drops.items():
                report_data[key] = DROP_TYPES[key](qs, records.count())

            LevelReport.objects.create(
                level=level,
                content_type=content_type,
                start_timestamp=records[records.count() - 1].timestamp,  # first() and last() do not work on sliced qs
                end_timestamp=records[0].timestamp,
                log_count=records.count(),
                unique_contributors=records.aggregate(Count('wizard_id', distinct=True))['wizard_id__count'],
                report=report_data,
            )

