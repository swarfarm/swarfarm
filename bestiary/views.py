from collections import OrderedDict

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseForbidden, JsonResponse
from django.shortcuts import render
from django.template import loader, RequestContext

from .models import *
from .forms import *
from .filters import MonsterFilter





def bestiary(request):
    name_search = request.POST.get('name-autocomplete')
    post_data = request.POST.copy()
    if name_search:
        post_data.update({'name': name_search})

    bestiary_filter_form = FilterMonsterForm(post_data or None)
    bestiary_filter_form.helper.form_action = reverse('bestiary:inventory')

    context = {
        'view': 'bestiary',
        'bestiary_filter_form': bestiary_filter_form,
    }
    context.update(_bestiary_inventory(request))

    if request.user.is_authenticated():
        context['profile_name'] = request.user.username

    return render(request, 'bestiary/base.html', context)


def bestiary_inventory(request):
    context = _bestiary_inventory(request)
    return render(request, 'bestiary/inventory.html', context)


def _bestiary_inventory(request):
    name_search = request.POST.get('name-autocomplete')
    post_data = request.POST.copy()

    if name_search:
        post_data.update({'name': name_search})

    monster_queryset = Monster.objects.filter(obtainable=True).select_related('awakens_from', 'awakens_to', 'leader_skill').prefetch_related('skills')
    form = FilterMonsterForm(post_data or None)

    # Get queryset sort options
    sort_options = request.POST.get('sort')
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
    page = request.POST.get('page')

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

    context = {
        'view': 'bestiary',
        'active_slug': monster_slug,
    }

    if request.user.is_authenticated():
        context['profile_name'] = request.user.username

    if monster.is_awakened and monster.awakens_from is not None:
        base_monster = monster.awakens_from
        awakened_monster = monster
    else:
        base_monster = monster
        awakened_monster = monster.awakens_to

    # Run some calcs to provide stat deltas between awakened and unawakened
    base_stats = base_monster.get_stats()
    context['family'] = monster.monster_family()

    context['base'] = {
        'mon': base_monster,
        'stats': base_stats,
        'leader_skill': base_monster.leader_skill,
        'skills': base_monster.skills.all().order_by('slot'),
    }

    if base_monster.awakens_to:
        awakened_stats = awakened_monster.get_stats()

        context['awakened'] = {
            'mon': awakened_monster,
            'stats': awakened_stats,
            'leader_skill': awakened_monster.leader_skill,
            'skills': awakened_monster.skills.all().order_by('slot'),
        }

        # Calculate change in stats as monster undergoes awakening
        if base_stats['6']['HP'] is not None and awakened_stats['6']['HP'] is not None:
            awakened_stats_deltas = dict()

            for stat, value in base_stats['6'].iteritems():
                if awakened_stats['6'][stat] != value:
                    awakened_stats_deltas[stat] = int(round((awakened_stats['6'][stat] / float(value)) * 100 - 100))

            if base_monster.speed != awakened_monster.speed:
                awakened_stats_deltas['SPD'] = awakened_monster.speed - base_monster.speed

            if base_monster.crit_rate != awakened_monster.crit_rate:
                awakened_stats_deltas['CRIT_Rate'] = awakened_monster.crit_rate - base_monster.crit_rate

            if base_monster.crit_damage != awakened_monster.crit_damage:
                awakened_stats_deltas['CRIT_DMG'] = awakened_monster.crit_damage - base_monster.crit_damage

            if base_monster.accuracy != awakened_monster.accuracy:
                awakened_stats_deltas['Accuracy'] = awakened_monster.accuracy - base_monster.accuracy

            if base_monster.resistance != awakened_monster.resistance:
                awakened_stats_deltas['Resistance'] = awakened_monster.resistance - base_monster.resistance

            context['awakened']['stat_deltas'] = awakened_stats_deltas

    return render(request, 'bestiary/detail_base.html', context)


def edit_skill(request, pk):
    skill = Skill.objects.get(pk=pk)
    form = SkillForm(request.POST or None, instance=skill)

    if request.user.is_superuser:
        template = loader.get_template('bestiary/edit_skill_form.html')

        if request.method == 'POST' and form.is_valid():
            form.save()
            response_data = {
                'code': 'success'
            }
        else:

            form.helper.form_action = reverse('bestiary:edit_skill', kwargs={'pk': pk})
            response_data = {
                'code': 'error',
                'html': template.render({'form': form}),
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden('Unauthorized')


def edit_monster(request):
    pass