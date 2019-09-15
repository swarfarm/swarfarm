from collections import Counter
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Min, Max, Avg, Sum, Func, F, Func, Q, CharField, FloatField, Value, StdDev
from django.db.models.functions import Cast, Concat, Extract
from django_pivot.histogram import histogram

from bestiary.models import Monster, Rune, Level, GameItem, Dungeon
from data_log import models
from data_log.util import slice_records, floor_to_nearest, ceil_to_nearest, replace_value_with_choice, \
    transform_to_dict, round_timedelta

MINIMUM_THRESHOLD = 0.005  # Any drops that occur less than this percentage of time are filtered out
CLEAR_TIME_BIN_WIDTH = timedelta(seconds=5)


def get_report_summary(drops, total_log_count, **kwargs):
    summary = {
        'table': {},
        'chart': [],
    }

    min_count = kwargs.get('min_count', max(1, int(MINIMUM_THRESHOLD * total_log_count)))

    # Chart data: list of {'drop': <string>, 'count': <int>}
    # Table data: dict (by drop type) of lists of items which drop, with stats. 'count' is only required stat.
    for drop_type, qs in drops.items():
        # Remove very low frequency occurrences from dataset
        qs = qs.annotate(count=Count('pk')).filter(count__gt=min_count)

        if drop_type == models.ItemDrop.RELATED_NAME:
            if kwargs.get('exclude_social_points'):
                qs = qs.exclude(item__category=GameItem.CATEGORY_CURRENCY, item__name='Social Point')

            chart_qs = qs.values(name=F('item__name')).annotate(count=Count('pk')).order_by('-count')

            if not kwargs.get('include_currency'):
                chart_qs = chart_qs.exclude(item__category=GameItem.CATEGORY_CURRENCY)

            chart_data = list(chart_qs)
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
                    qty_per_100=Cast(Sum('quantity'), FloatField()) / total_log_count * 100,
                ).order_by('item__category', '-count')
            )
        elif drop_type == models.MonsterDrop.RELATED_NAME:
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
                        stars=F('grade'),
                    ).annotate(
                        count=Count('pk'),
                        drop_chance=Cast(Count('pk'), FloatField()) / total_log_count * 100,
                        qty_per_100=Cast(Count('pk'), FloatField()) / total_log_count * 100,
                    )
                ),
                {'element': Monster.ELEMENT_CHOICES}
            )
        elif drop_type == models.RuneCraftDrop.RELATED_NAME:
            # Rune crafts are counted by type
            chart_data = list(
                replace_value_with_choice(
                    qs.values(
                        name=F('type'),
                    ).annotate(
                        count=Count('pk'),
                    ).order_by('-count'),
                    {'name': models.RuneCraftDrop.CRAFT_CHOICES}
                )
            )

            table_data = {
                'sets': replace_value_with_choice(
                    list(qs.values('rune').annotate(count=Count('pk')).order_by('rune')),
                    {'rune': Rune.TYPE_CHOICES}
                ),
                'type': replace_value_with_choice(
                    list(qs.values('type').annotate(count=Count('pk')).order_by('type')),
                    {'type': Rune.TYPE_CHOICES}
                ),
                'quality': replace_value_with_choice(
                    list(qs.values('quality').annotate(count=Count('pk')).order_by('quality')),
                    {'quality': Rune.QUALITY_CHOICES}
                ),
            }
        else:
            # Chart is name, count only
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
            if drop_type == models.MonsterPieceDrop.RELATED_NAME:
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
                            count=Count('pk'),
                            min=Min('quantity'),
                            max=Max('quantity'),
                            avg=Avg('quantity'),
                            drop_chance=Cast(Count('pk'), FloatField()) / total_log_count * 100,
                            qty_per_100=Cast(Sum('quantity'), FloatField()) / total_log_count * 100,
                        )
                    ),
                    {'element': Monster.ELEMENT_CHOICES}
                )
            elif drop_type == models.RuneDrop.RELATED_NAME:
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
            elif drop_type == models.RuneCraftDrop.RELATED_NAME:
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
            elif drop_type == models.DungeonSecretDungeonDrop.RELATED_NAME:
                table_data = replace_value_with_choice(
                    list(
                        qs.values(
                            name=F('level__dungeon__secretdungeon__monster__name'),
                            slug=F('level__dungeon__secretdungeon__monster__bestiary_slug'),
                            icon=F('level__dungeon__secretdungeon__monster__image_filename'),
                            element=F('level__dungeon__secretdungeon__monster__element'),
                            can_awaken=F('level__dungeon__secretdungeon__monster__can_awaken'),
                            is_awakened=F('level__dungeon__secretdungeon__monster__is_awakened'),
                            stars=F('level__dungeon__secretdungeon__monster__base_stars'),
                        ).annotate(
                            count=Count('pk'),
                            drop_chance=Cast(Count('pk'), FloatField()) / total_log_count * 100,
                            qty_per_100=Cast(Sum('pk'), FloatField()) / total_log_count * 100,
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


def get_item_report(qs, total_log_count, **kwargs):
    if qs.count() == 0:
        return None

    min_count = kwargs.get('min_count', max(1, int(MINIMUM_THRESHOLD * total_log_count)))

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
            qty_per_100=Cast(Sum('quantity'), FloatField()) / total_log_count * 100,
        ).filter(count__gt=min_count).order_by('-count')
    )

    return results


def get_monster_report(qs, total_log_count, **kwargs):
    if qs.count() == 0:
        return None

    min_count = kwargs.get('min_count', max(1, int(MINIMUM_THRESHOLD * total_log_count)))

    return {
        'monsters': {  # By unique monster
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                list(
                    qs.values(
                        'monster',
                    ).annotate(
                        monster_name=Func(
                            Concat(F('monster__element'), Value(' '), F('monster__name')),
                            function='INITCAP',
                        ),
                        count=Count('pk'),
                    ).filter(count__gt=min_count).order_by('-count')
                ),
                name_key='monster_name'
            ),
        },
        'family': {  # By family
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                list(
                    qs.values(
                        family_id=F('monster__family_id'),
                        name=F('monster__name'),
                    ).annotate(
                        count=Count('pk')
                    ).filter(
                        count__gt=min_count
                    ).order_by('-count')
                ),
                name_key='name'
            )
        },
        'nat_stars': {  # By nat stars
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                list(
                    qs.values(
                        nat_stars=F('monster__base_stars'),
                    ).annotate(
                        grade=Concat(Cast('monster__base_stars', CharField()), Value('⭐')),
                        count=Count('monster__base_stars'),
                    ).filter(count__gt=min_count).order_by('-count')
                ),
                name_key='grade'
            )
        },
        'element': {  # By element
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(
                        qs.values(
                            element=F('monster__element')
                        ).annotate(
                            element_cap=Func(F('monster__element'), function='INITCAP',),
                            count=Count('pk')
                        ).filter(count__gt=min_count).order_by('-count')
                    ),
                    {'element': Monster.ELEMENT_CHOICES}
                ),
                name_key='element_cap',
            )
        },
        'awakened': {  # By awakened/unawakened
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                list(
                    qs.values(
                        awakened=F('monster__is_awakened')
                    ).annotate(
                        count=Count('pk')
                    ).filter(count__gt=min_count).order_by('-count')
                ),
                transform={
                    True: 'Awakened',
                    False: 'Unawakened',
                }
            ),
        }
    }


def get_rune_report(qs, total_log_count, **kwargs):
    if qs.count() == 0:
        return None

    min_count = kwargs.get('min_count', max(1, int(MINIMUM_THRESHOLD * total_log_count)))

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
        'stars': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                list(
                    qs.values(
                        grade=Concat(Cast('stars', CharField()), Value('⭐'))
                    ).annotate(
                        count=Count('pk')
                    ).filter(count__gt=min_count).order_by('-count')
                )
            ),
        },
        'type': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('type').annotate(count=Count('pk')).filter(count__gt=min_count).order_by('-count')),
                    {'type': qs.model.TYPE_CHOICES}
                )
            ),
        },
        'quality': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('quality').annotate(count=Count('pk')).filter(count__gt=min_count).order_by('-count')),
                    {'quality': qs.model.QUALITY_CHOICES}
                )
            ),
        },
        'slot': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(list(qs.values('slot').annotate(count=Count('pk')).filter(count__gt=min_count).order_by('-count'))),
        },
        'main_stat': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('main_stat').annotate(count=Count('main_stat')).filter(count__gt=min_count).order_by('main_stat')),
                    {'main_stat': qs.model.STAT_CHOICES}
                )
            )
        },
        'slot_2_main_stat': {
            'type': 'occurrences',
            'total': qs.filter(slot=2).count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.filter(slot=2).values('main_stat').annotate(count=Count('main_stat')).filter(count__gt=min_count).order_by('main_stat')),
                    {'main_stat': qs.model.STAT_CHOICES}
                )
            )
        },
        'slot_4_main_stat': {
            'type': 'occurrences',
            'total': qs.filter(slot=4).count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.filter(slot=4).values('main_stat').annotate(count=Count('main_stat')).filter(
                        count__gt=min_count).order_by('main_stat')),
                    {'main_stat': qs.model.STAT_CHOICES}
                )
            )
        },
        'slot_6_main_stat': {
            'type': 'occurrences',
            'total': qs.filter(slot=6).count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.filter(slot=6).values('main_stat').annotate(count=Count('main_stat')).filter(
                        count__gt=min_count).order_by('main_stat')),
                    {'main_stat': qs.model.STAT_CHOICES}
                )
            )
        },
        'innate_stat': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('innate_stat').annotate(count=Count('pk')).filter(count__gt=min_count).order_by('innate_stat')),
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
            'width': 5,
            'data': histogram(qs, 'max_efficiency', range(0, 100, 5), slice_on='quality'),
        },
        'value': {
            'type': 'histogram',
            'width': 500,
            'data': histogram(qs, 'value', range(min_value, max_value, 500), slice_on='quality')
        }
    }


def _rune_craft_report_data(qs, total_log_count, **kwargs):
    if qs.count() == 0:
        return None

    min_count = kwargs.get('min_count', max(1, int(MINIMUM_THRESHOLD * total_log_count)))

    return {
        'type': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('type').annotate(count=Count('pk')).filter(count__gt=min_count).order_by('-count')),
                    {'type': qs.model.CRAFT_CHOICES}
                )
            ),
        },
        'rune': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('rune').annotate(count=Count('pk')).filter(count__gt=min_count).order_by('-count')),
                    {'rune': qs.model.TYPE_CHOICES}
                )
            ),
        },
        'quality': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('quality').annotate(count=Count('pk')).filter(count__gt=min_count).order_by('-count')),
                    {'quality': qs.model.QUALITY_CHOICES}
                )
            ),
        },
        'stat': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('stat').annotate(count=Count('stat')).filter(count__gt=min_count).order_by('stat')),
                    {'stat': qs.model.STAT_CHOICES}
                )
            )
        },
    }


def get_rune_craft_report(qs, total_log_count, **kwargs):
    return {
        'grindstone': _rune_craft_report_data(qs.filter(type__in=qs.model.CRAFT_GRINDSTONES), total_log_count, **kwargs),
        'gem': _rune_craft_report_data(qs.filter(type__in=qs.model.CRAFT_ENCHANT_GEMS), total_log_count, **kwargs),
    }


DROP_TYPES = {
    models.ItemDrop.RELATED_NAME: get_item_report,
    models.MonsterDrop.RELATED_NAME: get_monster_report,
    models.MonsterPieceDrop.RELATED_NAME: None,
    models.RuneDrop.RELATED_NAME: get_rune_report,
    models.RuneCraftDrop.RELATED_NAME: get_rune_craft_report,
    models.DungeonSecretDungeonDrop.RELATED_NAME: None,
}


def get_drop_querysets(qs):
    drop_querysets = {}

    for drop_type in DROP_TYPES.keys():
        # Get querysets for each possible drop type
        if hasattr(qs.model, drop_type):
            drop_model = getattr(qs.model, drop_type).field.model
            drop_querysets[drop_type] = drop_model.objects.filter(log__in=qs)

    return drop_querysets


def drop_report(qs, **kwargs):
    report_data = {}

    # Get querysets for each possible drop type
    drops = get_drop_querysets(qs)
    report_data['summary'] = get_report_summary(drops, qs.count(), **kwargs)

    # Clear time statistics, if supported by the qs model
    if hasattr(qs.model, 'clear_time'):
        successful_runs = qs.filter(
            Q(success=True) | Q(level__dungeon__category=Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS)
        )

        if successful_runs.count():
            clear_time_aggs = successful_runs.aggregate(
                std_dev=StdDev(Extract(F('clear_time'), lookup_name='epoch')),
                avg=Avg('clear_time'),
                min=Min('clear_time'),
                max=Max('clear_time'),
            )

            # Use +/- 3 std deviations of clear time avg as bounds for time range in case of extreme outliers skewing chart scale
            min_time = round_timedelta(
                max(clear_time_aggs['min'], clear_time_aggs['avg'] - timedelta(seconds=clear_time_aggs['std_dev'] * 3)),
                CLEAR_TIME_BIN_WIDTH,
                direction='down',
            )
            max_time = round_timedelta(
                min(clear_time_aggs['max'], clear_time_aggs['avg'] + timedelta(seconds=clear_time_aggs['std_dev'] * 3)),
                CLEAR_TIME_BIN_WIDTH,
                direction='up',
            )
            bins = [min_time + CLEAR_TIME_BIN_WIDTH * x for x in range(0, int((max_time - min_time) / CLEAR_TIME_BIN_WIDTH))]

            # Histogram generates on entire qs, not just successful runs.
            report_data['clear_time'] = {
                'min': str(clear_time_aggs['min']),
                'max': str(clear_time_aggs['max']),
                'avg': str(clear_time_aggs['avg']),
                'chart': {
                    'type': 'histogram',
                    'width': 5,
                    'data': histogram(qs, 'clear_time', bins, slice_on='success'),
                }
            }

    # Individual drop details
    for key, qs in drops.items():
        if DROP_TYPES[key]:
            report_data[key] = DROP_TYPES[key](qs, qs.count(), **kwargs)

    return report_data


def grade_summary_report(qs, grade_choices):
    report_data = []

    drops = get_drop_querysets(qs)

    # List of all drops. Currently only care about monsters and items
    all_items = GameItem.objects.filter(pk__in=drops['items'].values_list('item', flat=True)) if 'items' in drops else []
    all_monsters = Monster.objects.filter(pk__in=drops['monsters'].values_list('monster', flat=True)) if 'monsters' in drops else []
    all_runes = drops['runes'] if 'runes' in drops else []

    for grade_id, grade_name in grade_choices:
        grade_qs = qs.filter(grade=grade_id)
        grade_run_count = grade_qs.count() if grade_qs.count() else 1

        grade_report = {
            'grade': grade_name,
            'log_count': grade_qs.count(),
            'drops': [],
        }
        for item in all_items:
            result = drops['items'].filter(
                log__in=grade_qs,
                item=item,
            ).aggregate(
                count=Count('pk'),
                min=Min('quantity'),
                max=Max('quantity'),
                avg=Avg('quantity'),
                drop_chance=Cast(Count('pk'), FloatField()) / grade_run_count * 100,
                qty_per_100=Cast(Sum('quantity'), FloatField()) / grade_run_count * 100,
            )

            grade_report['drops'].append({
                'type': 'item',
                'name': item.name,
                'icon': item.icon,
                **result,
            })

        for monster in all_monsters:
            result = drops['monsters'].filter(
                log__in=grade_qs,
                monster=monster
            ).aggregate(
                count=Count('pk'),
                drop_chance=Cast(Count('pk'), FloatField()) / grade_run_count * 100,
                qty_per_100=Cast(Func(Count('pk'), 0, function='nullif'), FloatField()) / grade_run_count * 100,
            )

            grade_report['drops'].append({
                'type': 'monster',
                'name': monster.name,
                'icon': monster.image_filename,
                'stars': monster.base_stars,
                **result,
            })

        for stars in sorted(all_runes.values_list('stars', flat=True).distinct(), reverse=True):
            result = drops['runes'].filter(
                log__in=grade_qs,
                stars=stars,
            ).aggregate(
                count=Count('pk'),
                drop_chance=Cast(Count('pk'), FloatField()) / grade_run_count * 100,
                qty_per_100=Cast(Func(Count('pk'), 0, function='nullif'), FloatField()) / grade_run_count * 100,
            )

            grade_report['drops'].append({
                'type': 'rune',
                'name': f'{stars}⭐ Rune',
                **result,
            })

        report_data.append(grade_report)

    return report_data


def _generate_level_reports(model, **kwargs):
    content_type = ContentType.objects.get_for_model(model)
    levels = model.objects.values_list('level', flat=True).distinct().order_by()

    for level in Level.objects.filter(pk__in=levels):
        records = slice_records(model.objects.filter(level=level, success=True), minimum_count=2500, report_timespan=timedelta(weeks=2))

        if records.count() > 0:
            report_data = drop_report(records, **kwargs)

            models.LevelReport.objects.create(
                level=level,
                content_type=content_type,
                start_timestamp=records[records.count() - 1].timestamp,  # first() and last() do not work on sliced qs
                end_timestamp=records[0].timestamp,
                log_count=records.count(),
                unique_contributors=records.aggregate(Count('wizard_id', distinct=True))['wizard_id__count'],
                report=report_data,
            )


def generate_dungeon_log_reports(**kwargs):
    _generate_level_reports(models.DungeonLog, **kwargs)


def generate_rift_raid_reports():
    _generate_level_reports(models.RiftRaidLog, include_currency=True, exclude_social_points=True)


def _generate_by_grade_reports(model):
    content_type = ContentType.objects.get_for_model(model)
    levels = model.objects.values_list('level', flat=True).distinct().order_by()

    for level in Level.objects.filter(pk__in=levels):
        all_records = model.objects.none()
        report_data = {
            'reports': []
        }

        # Generate a report by grade
        for grade, grade_desc in model.GRADE_CHOICES:
            records = slice_records(model.objects.filter(level=level, grade=grade), minimum_count=2500, report_timespan=timedelta(weeks=2))

            if records.count() > 0:
                grade_report = drop_report(records)
            else:
                grade_report = None

            report_data['reports'].append({
                'grade': grade_desc,
                'report': grade_report
            })
            all_records |= records

        if all_records.count() > 0:
            # Generate a report with all results for a complete list of all things that drop here
            report_data['summary'] = grade_summary_report(all_records, model.GRADE_CHOICES)

            models.LevelReport.objects.create(
                level=level,
                content_type=content_type,
                start_timestamp=all_records.last().timestamp,
                end_timestamp=all_records.first().timestamp,
                log_count=all_records.count(),
                unique_contributors=all_records.aggregate(Count('wizard_id', distinct=True))['wizard_id__count'],
                report=report_data,
            )


def generate_rift_dungeon_reports():
    _generate_by_grade_reports(models.RiftDungeonLog)


def generate_world_boss_dungeon_reports():
    _generate_by_grade_reports(models.WorldBossLog)