from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse

from .filters import MonsterFilter
from .forms import FilterMonsterForm
from .models import Monster


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
