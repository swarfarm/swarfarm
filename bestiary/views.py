from collections import OrderedDict

from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect, get_object_or_404

from herders.models import Monster
from herders.forms import FilterMonsterForm
from herders.filters import MonsterFilter


def bestiary(request):
    bestiary_filter_form = FilterMonsterForm()
    bestiary_filter_form.helper.form_action = reverse('bestiary:inventory')

    context = {
        'view': 'bestiary',
        'bestiary_filter_form': bestiary_filter_form,
    }

    if request.user.is_authenticated():
        context['profile_name'] = request.user.username

    return render(request, 'bestiary/base.html', context)


def bestiary_inventory(request):
    monster_queryset = Monster.objects.filter(obtainable=True).select_related('awakens_from', 'awakens_to', 'leader_skill').prefetch_related('skills', 'skills__skill_effect')
    form = FilterMonsterForm(request.POST or None)

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

    return render(request, 'bestiary/inventory.html', context)


def bestiary_detail(request, monster_slug):
    monster = Monster.objects.filter(bestiary_slug=monster_slug).first()

    if monster is None:
        raise Http404()

    context = {
        'view': 'bestiary',
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
    context['base_monster'] = base_monster
    context['base_monster_stats'] = base_stats
    context['base_monster_leader_skill'] = base_monster.leader_skill
    context['base_monster_skills'] = base_monster.skills.all().order_by('slot')

    if base_monster.awakens_to:
        awakened_stats = awakened_monster.get_stats()

        # Calculate change in stats as monster undergoes awakening
        if base_stats['6']['1']['HP'] is not None and awakened_stats['6']['1']['HP'] is not None:
            awakened_stats_deltas = dict()

            for stat, value in base_stats['6']['40'].iteritems():
                if awakened_stats['6']['40'][stat] != value:
                    awakened_stats_deltas[stat] = int(round((awakened_stats['6']['40'][stat] / float(value)) * 100 - 100))

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

            context['awakened_monster_stats_deltas'] = awakened_stats_deltas

        context['awakened_monster'] = awakened_monster
        context['awakened_monster_stats'] = awakened_stats
        context['awakened_monster_leader_skill'] = awakened_monster.leader_skill
        context['awakened_monster_skills'] = awakened_monster.skills.all().order_by('slot')

    return render(request, 'bestiary/detail.html', context)


def bestiary_sanity_checks(request):
    from herders.models import MonsterSkill

    if request.user.is_staff:
        errors = OrderedDict()
        monsters = Monster.objects.filter(obtainable=True)

        for monster in monsters:
            monster_errors = []

            # Check for missing skills
            if monster.skills.count() == 0:
                monster_errors.append('Missing skills')

            # Check for same slot
            for slot in range(1, 5):
                if monster.skills.all().filter(slot=slot).count() > 1:
                    monster_errors.append("More than one skill in slot " + str(slot))

            # Check for missing stats
            if monster.base_hp is None:
                monster_errors.append('Missing base HP')

            if monster.base_attack is None:
                monster_errors.append('Missing base ATK')
            if monster.base_defense is None:
                monster_errors.append('Missing base DEF')
            if monster.speed is None:
                monster_errors.append('Missing SPD')
            if monster.crit_damage is None:
                monster_errors.append('Missing crit DMG')
            if monster.crit_rate is None:
                monster_errors.append('Missing crit rate')
            if monster.resistance is None:
                monster_errors.append('Missing resistance')
            if monster.accuracy is None:
                monster_errors.append('Missing accuracy')

            # Check missing links resource
            if monster.can_awaken and monster.archetype != monster.TYPE_MATERIAL and (monster.summonerswar_co_url is None or monster.summonerswar_co_url == ''):
                monster_errors.append('Missing summonerswar.co link')

            if monster.wikia_url is None or monster.wikia_url == '':
                monster_errors.append('Missing wikia link')

            # Check missing skills
            if monster.source.count() == 0:
                monster_errors.append('Missing sources')

            # Check that monster has awakening mats specified
            if monster.can_awaken and not monster.is_awakened and monster.awaken_mats_magic_high + monster.awaken_mats_magic_low + monster.awaken_mats_magic_mid == 0:
                monster_errors.append('Missing awakening materials')

            if len(monster_errors) > 0:
                errors[str(monster)] = monster_errors

        prev_skill_slot = 0
        for skill in MonsterSkill.objects.all():
            skill_errors = []

            # Check that skill slots are not skipped
            if skill.slot - prev_skill_slot > 1 and prev_skill_slot >= 1:
                skill_errors.append('slot skipped from previous skill')
            prev_skill_slot = skill.slot

            # Check that skill has a level up description if it is not a passive
            if not skill.passive and skill.max_level == 1:
                skill_errors.append('max level missing for non-passive skill')

            # Check that skill has a cooltime if it is not a passive
            if not skill.passive and not skill.cooltime:
                skill_errors.append('Cooltime missing for non-passive skill')

            # Check max level of skill = num lines in level up progress + 1
            if skill.max_level > 1:
                line_count = len(skill.level_progress_description.split('\r\n'))

                if skill.max_level != line_count + 1:
                    skill_errors.append('inconsistent level up text and max level')

            # Check that skill is used
            if skill.monster_set.count() == 0:
                skill_errors.append('unused skill')

            # Check passives are in slot 3 (with some exceptions)
            if skill.passive and skill.slot != 3:
                if skill.monster_set.first().archetype != Monster.TYPE_MATERIAL:
                    skill_errors.append('passive not in slot 3')

            # Check missing skill description
            if 'Missing' in skill.level_progress_description:
                skill_errors.append('missing level-up description and possibly max level.')

            if len(skill_errors) > 0:
                errors[str(skill)] = skill_errors

        return render(request, 'herders/skill_debug.html', {'errors': errors})
