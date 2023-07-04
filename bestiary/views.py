from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Q
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .filters import MonsterFilter
from .forms import FilterMonsterForm
from .models import Monster, Dungeon, Level, Wave, Enemy
from data_log.models import DungeonLog, RiftDungeonLog, RiftRaidLog, WorldBossLog
from data_log.reports.generate import _generate_level_report, _generate_by_grade_report

from datetime import datetime, timedelta


def bestiary(request):
    name_search = request.GET.get('name-autocomplete')
    post_data = request.GET.copy()
    if name_search:
        post_data.update({'name': name_search})

    bestiary_filter_form = FilterMonsterForm(post_data or None)
    bestiary_filter_form.helper.form_action = reverse('bestiary:inventory')

    context = {
        'view': 'bestiary',
        'bestiary_filter_form': bestiary_filter_form,
        'init_load': True,
    }

    if request.user.is_authenticated:
        context['profile_name'] = request.user.username

    return render(request, 'bestiary/base.html', context)


def bestiary_inventory(request):
    context = _bestiary_inventory(request)
    return render(request, 'bestiary/inventory.html', context)


def _bestiary_inventory(request):
    name_search = request.GET.get('name-autocomplete')
    post_data = request.GET.copy()

    if name_search:
        post_data.update({'name': name_search})

    monster_queryset = Monster.objects.filter(obtainable=True).select_related('awakens_from', 'awakens_to', 'leader_skill').prefetch_related('skills')
    form = FilterMonsterForm(post_data or None)

    # Get queryset sort options
    sort_options = request.GET.get('sort')
    if sort_options:
        sort_col_match = {
            'name': 'name',
            'stars': 'base_stars',
            'element': 'element',
            'archetype': 'archetype',
            'awakens-to': 'awakens_to__name',
            'awakens-from': 'awakens_from__name',
            'leader-skill': 'leader_skill__amount',
            'hp-lv40': 'max_lvl_hp',
            'def-lv40': 'max_lvl_defense',
            'atk-lv40': 'max_lvl_attack',
            'spd': 'speed',
            'cri-rate': 'crit_rate',
            'cri-dmg': 'crit_damage',
            'res': 'resistance',
            'acc': 'accuracy',
            'skill-ups-reqd': 'skill_ups_to_max'
        }
        sort_direction_match = {
            'asc': '',
            'desc': '-',
        }
        sort_options = sort_options.split(';')
        sort_col = sort_col_match.get(sort_options[0])
        sort_direction = sort_direction_match.get(sort_options[1])

        if sort_col and sort_direction is not None:
            monster_queryset = monster_queryset.order_by(sort_direction + sort_col)

    if form.is_valid():
        monster_filter = MonsterFilter(form.cleaned_data, queryset=monster_queryset)
    else:
        monster_filter = MonsterFilter(queryset=monster_queryset)

    paginator = Paginator(monster_filter.qs, 100)
    page = request.GET.get('page')

    try:
        monsters = paginator.page(page)
    except PageNotAnInteger:
        monsters = paginator.page(1)
    except EmptyPage:
        monsters = paginator.page(paginator.num_pages)

    context = {
        'monsters': monsters,
        'page_range': paginator.page_range,
    }

    return context


def bestiary_detail(request, monster_slug):
    monster = Monster.objects.filter(bestiary_slug=monster_slug).first()

    if monster is None:
        raise Http404()

    mon = monster.base_monster
    monsters = []

    while mon is not None:
        monsters.append(mon)
        mon = mon.awakens_to

    context = {
        'view': 'bestiary',
        'active_slug': monster_slug,
        'family': monster.monster_family(),
        'monsters': monsters,
    }

    if request.user.is_authenticated:
        context['profile_name'] = request.user.username

    return render(request, 'bestiary/detail_base.html', context)


def dungeons(request):
    context = {
        'view': 'dungeons',
        'dungeons': {},
    }

    for cat_id, category in Dungeon.CATEGORY_CHOICES:
        d = Dungeon.objects.filter(
            category=cat_id,
            enabled=True
        ).exclude(
            Q(category=Dungeon.CATEGORY_SECRET) | Q(slug='dimension-predator')
        ).prefetch_related(
            'level_set',
        )
        # push Hall of [element] to the end
        if cat_id == Dungeon.CATEGORY_CAIROS:
            d_s = []
            halls = []
            for dung in d:
                if 'hall-of-' in dung.slug:
                    halls.append(dung)
                else:
                    d_s.append(dung)
            d_s += halls
            if len(d_s) > 0:
                context['dungeons'][category] = d_s
        else:
            if d.count() > 0:
                context['dungeons'][category] = d

    return render(request, 'dungeons/base.html', context)


def dungeon_detail(request, slug, difficulty=None, floor=None):
    dung = get_object_or_404(Dungeon.objects.all().prefetch_related('level_set'), slug=slug)
    lvl = None
    levels = dung.level_set.all()

    if difficulty:
        difficulty_id = {v.lower(): k for k, v in dict(Level.DIFFICULTY_CHOICES).items()}.get(difficulty)

        if difficulty_id is None:
            raise Http404()

        levels = levels.filter(difficulty=difficulty_id)

    if floor:
        levels = levels.filter(floor=floor)
    else:
        # Pick first hell level for scenarios, otherwise always last level
        if dung.category == Dungeon.CATEGORY_SCENARIO:
            lvl = levels.filter(difficulty=Level.DIFFICULTY_HELL).first()
            return redirect('bestiary:dungeon_detail_difficulty', slug=dung.slug, difficulty='hell', floor=lvl.floor)
        else:
            lvl = levels.last()

            # Redirect to URL with floor if dungeon has more than 1 floor
            if dung.level_set.count() > 1:
                return redirect('bestiary:dungeon_detail', slug=dung.slug, floor=1)

    if not lvl:
        # Default to first level for all others
        lvl = levels.first()

    if not lvl:
        raise Http404()

    found_by_date = None
    dungeon_log_mapper = {
        Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS: {
            'log': RiftDungeonLog,
            'func': _generate_by_grade_report,
        },
        Dungeon.CATEGORY_RIFT_OF_WORLDS_RAID: {
            'log': RiftRaidLog,
            'func': _generate_level_report,
        },
        Dungeon.CATEGORY_WORLD_BOSS: {
            'log': RiftDungeonLog,
            'func': _generate_by_grade_report,
        },
        'default': {
            'log': DungeonLog,
            'func': _generate_level_report,
        },
    }
    try:
        start_date = request.GET.get('start_date', None)
        end_date = request.GET.get('end_date', None)
        now = timezone.now()

        report = None
        try:
            if start_date:
                start_date = timezone.make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
            if end_date:
                end_date = timezone.make_aware(datetime.strptime(end_date, "%Y-%m-%d"))
                end_date = min(end_date, now)
        except ValueError:
            start_date = None
            end_date = None

        if start_date and end_date: 
            report = lvl.logs.filter(
                start_timestamp__date=start_date.date(),
                end_timestamp__date=end_date.date(),
            ).first()
            if not report:
                dung_log = dungeon_log_mapper.get(dung.category, dungeon_log_mapper.get('default'))
                report = dung_log['func'](
                    level=lvl, 
                    model=dung_log['log'],
                    content_type=ContentType.objects.get_for_model(dung_log['log']),
                    start_date=start_date,
                    end_date=end_date,
                )
            found_by_date = True
        
        if not report:
            report = lvl.logs.filter(
                start_timestamp__gte=now - timedelta(weeks=2),
                end_timestamp__lte=now,
            ).first() or lvl.logs.latest()
            if start_date and end_date:
                found_by_date = False
    except lvl.logs.model.DoesNotExist:
        report = None

    floor_range = range(
        1,
        dung.level_set.aggregate(Max('floor'))['floor__max'] + 1
    )

    context = {
        'view': 'dungeons',
        'dungeon': dung,
        'floor_range': floor_range,
        'is_scenario': dung.category == Dungeon.CATEGORY_SCENARIO,
        'level': lvl,
        'report': report,
        'waves': Wave.objects.filter(level=lvl).prefetch_related('enemy_set', 'enemy_set__monster'),
        'found_by_date': found_by_date,
        'start_date': start_date.strftime("%Y-%m-%d") if start_date else None,
        'end_date': end_date.strftime("%Y-%m-%d") if start_date else None,
    }

    by_grade = dung.category in [Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS, Dungeon.CATEGORY_WORLD_BOSS]

    if by_grade and report and hasattr(report.content_type.model_class(), 'GRADE_CHOICES'):
        return render(request, 'dungeons/detail/report_by_grade.html', context)
    else:
        return render(request, 'dungeons/detail/report.html', context)
