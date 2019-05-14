from collections import Counter
from datetime import timedelta
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Min, Max, Avg, Sum, Func, F, CharField, FloatField, Value
from django.db.models.functions import Cast, Concat
from django_pivot.histogram import histogram

from bestiary.models import Monster, Rune, RuneCraft, Dungeon, Level, GameItem
from data_log.models import Report, LevelReport, SummonLog, DungeonLog, ItemDrop, MonsterDrop, MonsterPieceDrop, RuneDrop, RuneCraftDrop, DungeonSecretDungeonDrop
from data_log.util import floor_to_nearest, ceil_to_nearest, replace_value_with_choice, transform_to_dict


def _records_to_report(qs, report_timespan=timedelta(weeks=2), minimum_count=2500):
    if qs.filter(timestamp__gte=timezone.now() - report_timespan).count() < minimum_count:
        # Return latest minimum_count logs, ignoring report timespan
        return qs[:minimum_count]
    else:
        return qs.filter(timestamp__gte=timezone.now() - report_timespan)


def get_report_summary(drops, total_log_count):
    summary = {
        'table': {},
        'chart': [],
    }

    # Chart data: list of {'drop': <string>, 'count': <int>}
    # Table data: dict (by drop type) of lists of items which drop, with stats. 'count' is only required stat.
    for drop_type, qs in drops.items():
        if drop_type == ItemDrop.RELATED_NAME:
            # Chart excludes currency
            chart_data = list(
                qs.exclude(
                    item__category=GameItem.CATEGORY_CURRENCY,
                ).values(
                    name=F('item__name'),
                ).annotate(
                    count=Count('pk'),
                ).filter(count__gt=0).order_by('-count')
            )

            table_data = list(
                qs.values(
                    name=F('item__name'),
                    icon=F('item__icon'),
                ).annotate(
                    count=Count('pk'),
                    min=Min('quantity'),
                    max=Max('quantity'),
                    avg=Avg('quantity'),
                    drop_chance=Cast(Count('pk'), FloatField()) / total_log_count * 100,
                    avg_per_run=Cast(Sum('quantity'), FloatField()) / total_log_count,
                ).filter(count__gt=0).order_by('item__category', '-count')
            )
        elif drop_type == MonsterDrop.RELATED_NAME:
            # Monster drops in chart are counted by stars
            chart_data = list(
                qs.values(
                    name=Concat(Cast('grade', CharField()), Value('⭐ Monster'))
                ).annotate(
                    count=Count('pk')
                ).filter(count__gt=0).order_by('-count')
            )

            table_data = replace_value_with_choice(
                list(
                    qs.values(
                        name=F('monster__name'),
                        slug=F('monster__bestiary_slug'),
                        icon=F('monster__image_filename'),
                        element=F('monster__element'),
                        can_awaken=F('monster__can_awaken'),
                        is_awakened=F('monster__is_awakened'),
                        stars=F('monster__base_stars'),
                    ).annotate(
                        count=Count('pk'),
                        drop_chance=Cast(Count('pk'), FloatField()) / total_log_count * 100,
                    )
                ),
                {'element': Monster.ELEMENT_CHOICES}
            )
        else:
            # Chart can is name, count only
            item_name = ' '.join([s.capitalize() for s in drop_type.split('_')]).rstrip('s')
            count = qs.aggregate(count=Count('pk'))['count']
            if count > 0:
                chart_data = [{
                    'name': item_name,
                    'count': count,
                }]
            else:
                chart_data = []

            # Table data based on item type
            if drop_type == MonsterPieceDrop.RELATED_NAME:
                table_data = replace_value_with_choice(
                    list(
                        qs.values(
                            name=F('monster__name'),
                            icon=F('monster__image_filename'),
                            element=F('monster__element'),
                            count=Count('pk'),
                            min=Min('quantity'),
                            max=Max('quantity'),
                            avg=Avg('quantity'),
                        )
                    ),
                    {'element': Monster.ELEMENT_CHOICES}
                )
            elif drop_type == RuneDrop.RELATED_NAME:
                table_data = {
                    'sets': replace_value_with_choice(
                        list(qs.values('type').annotate(count=Count('pk')).order_by('type')),
                        {'type': Rune.TYPE_CHOICES}
                    ),
                    'slots': list(qs.values('slot').annotate(count=Count('pk')).order_by('slot')),
                    'quality': replace_value_with_choice(
                        list(qs.values('quality').annotate(count=Count('pk')).order_by('quality')),
                        {'quality': Rune.QUALITY_CHOICES}
                    ),
                }
            elif drop_type == RuneCraftDrop.RELATED_NAME:
                table_data = replace_value_with_choice(
                    list(
                        qs.values(
                            'type', 'rune', 'quality'
                        ).annotate(
                            count=Count('pk'),
                        ).order_by('type', 'rune', 'quality')
                    ),
                    {'type': Rune.TYPE_CHOICES, 'quality': Rune.QUALITY_CHOICES}
                )
            elif drop_type == DungeonSecretDungeonDrop.RELATED_NAME:
                table_data = replace_value_with_choice(
                    list(
                        qs.values(
                            name=F('level__dungeon__secretdungeon__monster__name'),
                            element=F('level__dungeon__secretdungeon__monster__element'),
                            icon=F('level__dungeon__secretdungeon__monster__image_filename'),
                        ).annotate(
                            count=Count('pk'),
                        )
                    ),
                    {'element': Monster.ELEMENT_CHOICES}
                )

            else:
                raise NotImplementedError(f"No summary table generation for {drop_type}")

        summary['chart'] += chart_data

        if table_data:
            summary['table'][drop_type] = table_data

    return summary


def get_item_report(qs, total_log_count):
    if qs.count() == 0:
        return None

    results = list(
        qs.values(
            'item',
            name=F('item__name'),
            icon=F('item__icon'),
        ).annotate(
            count=Count('pk'),
            min=Min('quantity'),
            max=Max('quantity'),
            avg=Avg('quantity'),
            drop_chance=Cast(Count('pk'), FloatField()) / total_log_count * 100,
            avg_per_run=Cast(Sum('quantity'), FloatField()) / total_log_count,
        ).order_by('-count')
    )

    return results


def get_monster_report(qs, total_log_count):
    if qs.count() == 0:
        return None

    results = {}

    # By unique monster
    results['monsters'] = {
        'type': 'occurrences',
        'total': qs.count(),
        'data': list(qs.values(
            'monster',
            name=F('monster__name'),
            element=F('monster__element'),
            com2us_id=F('monster__com2us_id'),
            icon=F('monster__image_filename')
        ).annotate(count=Count('pk')))
    }

    # By family
    results['family'] = {
        'type': 'occurrences',
        'total': qs.count(),
        'data': list(qs.values(
            family_id=F('monster__family_id'),
            name=F('monster__name'),
        ).annotate(count=Count('pk')))
    }

    # By nat stars
    mons_by_nat_stars = list(
        qs.values(
            nat_stars=F('monster__base_stars'),
        ).annotate(
            count=Count('monster__base_stars'),
            drop_chance=Cast(Count('pk'), FloatField()) / total_log_count * 100,
        )
    )

    results['nat_stars'] = {
        'type': 'occurrences',
        'total': qs.count(),
        'data': mons_by_nat_stars,
    }

    # By element
    results['element'] = {
        'type': 'occurrences',
        'total': qs.count(),
        'data': replace_value_with_choice(
            list(qs.values(element=F('monster__element')).annotate(count=Count('pk'))),
            {'element': Monster.ELEMENT_CHOICES}
        )
    }

    # By awakened/unawakened
    results['awakened'] = {
        'type': 'occurrences',
        'total': qs.count(),
        'data': list(qs.values(awakened=F('monster__is_awakened')).annotate(count=Count('pk'))),
    }

    return results


def get_monster_piece_report(qs, total_log_count):
    return "monster piece report"


def get_rune_report(qs, total_log_count):
    if qs.count() == 0:
        return None

    # Substat distribution
    # Unable to use database aggregation on an ArrayField without ORM gymnastics, so post-process data in python
    all_substats = qs.annotate(
        flat_substats=Func(F('substats'), function='unnest')
    ).values_list('flat_substats', flat=True)
    substat_counts = Counter(all_substats)

    # Sell value ranges
    min_value, max_value = qs.aggregate(Min('value'), Max('value')).values()
    min_value = int(floor_to_nearest(min_value, 1000))
    max_value = int(ceil_to_nearest(max_value, 1000))

    return {
        'total_count': qs.count(),
        'stars': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(list(qs.values('stars').annotate(count=Count('pk')).order_by('-count'))),
        },
        'type': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('type').annotate(count=Count('pk')).order_by('-count')),
                    {'type': qs.model.TYPE_CHOICES}
                )
            ),
        },
        'quality': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('quality').annotate(count=Count('pk')).order_by('-count')),
                    {'quality': qs.model.QUALITY_CHOICES}
                )
            ),
        },
        'slot': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(list(qs.values('slot').annotate(count=Count('pk')).order_by('-count'))),
        },
        'main_stat': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('main_stat').annotate(count=Count('main_stat')).order_by('main_stat')),
                    {'main_stat': qs.model.STAT_CHOICES}
                )
            )
        },
        'innate_stat': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('innate_stat').annotate(count=Count('pk')).order_by('innate_stat')),
                    {'innate_stat': qs.model.STAT_CHOICES}
                )
            )
        },
        'substats': {
            'type': 'occurrences',
            'total': len(all_substats),
            'data': transform_to_dict(
                replace_value_with_choice(
                    sorted(
                        [{'substat': k, 'count': v} for k, v in substat_counts.items()],
                        key=lambda count: count['substat']
                    ),
                    {'substat': qs.model.STAT_CHOICES}
                ),
            )
        },
        'max_efficiency': {
            'type': 'histogram',
            'data': histogram(qs, 'max_efficiency', range(0, 100, 5), slice_on='quality'),
        },
        'value': {
            'type': 'histogram',
            'data': histogram(qs, 'value', range(min_value, max_value, 250), slice_on='quality')
        }
    }


def get_rune_craft_report(qs, total_log_count):
    return "rune craft report"


def get_secret_dungeon_report(qs, total_log_count):
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


def generate_level_reports():
    content_type = ContentType.objects.get_for_model(DungeonLog)

    for level in Level.objects.all():
        records = _records_to_report(DungeonLog.objects.filter(level=level))

        if records.count() > 0:
            report_data = {}

            # Get querysets for each possible drop type
            drops = get_drop_querysets(records)
            report_data['summary'] = get_report_summary(drops, records.count())

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

