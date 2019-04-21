from datetime import timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Min, Max, Avg

from bestiary.models import Dungeon, Level
from .models import Report, LevelReport, SummonLog, DungeonLog, ItemDrop, MonsterDrop, MonsterPieceDrop, RuneDrop, RuneCraftDrop, DungeonSecretDungeonDrop


def _records_to_report(qs, report_timespan=timedelta(weeks=2), minimum_count=2500):
    if qs.filter(timestamp__gte=timezone.now() - report_timespan).count() < minimum_count:
        # Return latest minimum_count logs, ignoring report timespan
        return qs[:minimum_count]
    else:
        return qs.filter(timestamp__gte=timezone.now() - report_timespan)


DROP_TYPES = [
    ItemDrop.RELATED_NAME,
    MonsterDrop.RELATED_NAME,
    MonsterPieceDrop.RELATED_NAME,
    RuneDrop.RELATED_NAME,
    RuneCraftDrop.RELATED_NAME,
    DungeonSecretDungeonDrop.RELATED_NAME,
]


def get_drop_querysets(qs):
    drop_querysets = {}

    for drop_type in DROP_TYPES:
        # Get querysets for each possible drop type
        if hasattr(qs.model, drop_type):
            drop_model = getattr(qs.model, drop_type).field.model
            drop_querysets[drop_type] = drop_model.objects.filter(log__in=qs)

    return drop_querysets


def get_report_summary(drops):
    summary = {}

    for drop_type, qs in drops.items():
        if drop_type == ItemDrop.RELATED_NAME:
            # Item drops are counted individually and contain quantity information
            summary_data = list(qs.values(
                'item',
                'item__name',
                'item__icon'
            ).annotate(
                count=Count('item'),
                min=Min('quantity'),
                max=Max('quantity'),
                avg=Avg('quantity')
            ))
        elif drop_type == MonsterDrop.RELATED_NAME:
            # Monster drops are counted by stars
            summary_data = list(qs.values('grade').annotate(count=Count('pk')))
        else:
            # Count only
            summary_data = qs.aggregate(count=Count('pk'))

        summary[drop_type] = summary_data

    return summary


def generate_scenario_reports():
    content_type = ContentType.objects.get_for_model(DungeonLog)

    for level in Level.objects.filter(
            dungeon__category=Dungeon.CATEGORY_SCENARIO,
    ):
        print(level)
        records = _records_to_report(DungeonLog.objects.filter(level=level), minimum_count=5)

        if records.count() > 0:
            report_data = {}

            # Unique contributors


            # Get querysets for each possible drop type
            item_drops = get_drop_querysets(records)

            # Summary of data
            report_data['summary'] = get_report_summary(item_drops)

            LevelReport.objects.create(
                level=level,
                content_type=content_type,
                start_timestamp=records[records.count() - 1].timestamp,  # first() and last() do not work on sliced qs
                end_timestamp=records[0].timestamp,
                log_count=records.count(),
                unique_contributors=records.aggregate(Count('wizard_id', distinct=True))['wizard_id__count'],
                report=report_data,
            )
