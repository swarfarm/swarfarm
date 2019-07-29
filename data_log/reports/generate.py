from collections import Counter
from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db.models import Count, Min, Max, Avg, Sum, Func, F, CharField, FloatField, Value
from django.db.models.functions import Cast, Concat
from django.utils import timezone
from django_pivot.histogram import histogram

from bestiary.models import Monster, Rune, Level, GameItem
from data_log import models
from data_log.util import floor_to_nearest, ceil_to_nearest, replace_value_with_choice, transform_to_dict


def _records_to_report(qs, report_timespan=timedelta(weeks=2), minimum_count=2500):
    if qs.filter(timestamp__gte=timezone.now() - report_timespan).count() < minimum_count:
        # Want to avoid slicing due to restrictions on any subsequent queryset operations
        # Find the timestamp of the 2500th record and then filter on timestamp
        results = qs[:minimum_count]

        if results.count() > 0:
            earliest_record = results[results.count() - 1]
            return qs.filter(timestamp__gte=earliest_record.timestamp)
        else:
            # Don't have any records so just return it as is
            return qs
    else:
        return qs.filter(timestamp__gte=timezone.now() - report_timespan)


def get_report_summary(drops, total_log_count, **kwargs):
    summary = {
        'table': {},
        'chart': [],
    }

    # Chart data: list of {'drop': <string>, 'count': <int>}
    # Table data: dict (by drop type) of lists of items which drop, with stats. 'count' is only required stat.
    for drop_type, qs in drops.items():
        if drop_type == models.ItemDrop.RELATED_NAME:
            chart_qs = qs.values(name=F('item__name')).annotate(count=Count('pk')).filter(count__gt=0).order_by('-count')

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
                ).filter(count__gt=0).order_by('item__category', '-count')
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
            qty_per_100=Cast(Sum('quantity'), FloatField()) / total_log_count * 100,
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
            qty_per_100=Cast(Func(Count('pk'), 0, function='nullif'), FloatField()) / total_log_count * 100,
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
        'stars': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                list(
                    qs.values(
                        grade=Concat(Cast('stars', CharField()), Value('⭐'))
                    ).annotate(
                        count=Count('pk')
                    ).order_by('-count')
                )
            ),
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
            'width': 5,
            'data': histogram(qs, 'max_efficiency', range(0, 100, 5), slice_on='quality'),
        },
        'value': {
            'type': 'histogram',
            'width': 500,
            'data': histogram(qs, 'value', range(min_value, max_value, 500), slice_on='quality')
        }
    }


def _rune_craft_report_data(qs):
    if qs.count() == 0:
        return None

    return {
        'type': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('type').annotate(count=Count('pk')).order_by('-count')),
                    {'type': qs.model.CRAFT_CHOICES}
                )
            ),
        },
        'rune': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('rune').annotate(count=Count('pk')).order_by('-count')),
                    {'rune': qs.model.TYPE_CHOICES}
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
        'stat': {
            'type': 'occurrences',
            'total': qs.count(),
            'data': transform_to_dict(
                replace_value_with_choice(
                    list(qs.values('stat').annotate(count=Count('stat')).order_by('stat')),
                    {'stat': qs.model.STAT_CHOICES}
                )
            )
        },
    }


def get_rune_craft_report(qs, total_log_count):
    return {
        'grindstone': _rune_craft_report_data(qs.filter(type__in=qs.model.CRAFT_GRINDSTONES)),
        'gem': _rune_craft_report_data(qs.filter(type__in=qs.model.CRAFT_ENCHANT_GEMS)),
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


def level_drop_report(qs, **kwargs):
    report_data = {}

    # Get querysets for each possible drop type
    drops = get_drop_querysets(qs)
    report_data['summary'] = get_report_summary(drops, qs.count(), **kwargs)

    for key, qs in drops.items():
        if DROP_TYPES[key]:
            report_data[key] = DROP_TYPES[key](qs, qs.count())

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
        records = _records_to_report(model.objects.filter(level=level, success=True))

        if records.count() > 0:
            report_data = level_drop_report(records, **kwargs)

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
    _generate_level_reports(models.RiftRaidLog, include_currency=True)


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
            records = _records_to_report(model.objects.filter(level=level, grade=grade))

            if records.count() > 0:
                grade_report = level_drop_report(records)
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