from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Max, Q
from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from .filters import MonsterFilter
from .forms import FilterMonsterForm
from .models import Monster, Dungeon, Level, Wave, Enemy


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
            'type': 'archetype',
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
            # Prefetch('level_set', queryset=Level.objects.normal(), to_attr='normal'),
            # Prefetch('level_set', queryset=Level.objects.hard(), to_attr='hard'),
            # Prefetch('level_set', queryset=Level.objects.hell(), to_attr='hell'),
        )

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

    try:
        report = lvl.logs.latest()
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
    }

    by_grade = dung.category in [Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS, Dungeon.CATEGORY_WORLD_BOSS]

    if by_grade and report and hasattr(report.content_type.model_class(), 'GRADE_CHOICES'):
        return render(request, 'dungeons/detail/report_by_grade.html', context)
    else:
        return render(request, 'dungeons/detail/report.html', context)
