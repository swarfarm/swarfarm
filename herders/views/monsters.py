from collections import OrderedDict
import itertools
from operator import getitem 

from crispy_forms.bootstrap import FieldWithButtons, StrictButton, Field, Div
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Q, Count
from django.forms.models import modelformset_factory
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.template.context_processors import csrf
from django.urls import reverse

from bestiary.models import Monster, Building, Fusion, ESSENCE_MAP, GameItem
from herders.decorators import username_case_redirect
from herders.filters import MonsterInstanceFilter
from herders.forms import CompareMonstersForm, FilterMonsterInstanceForm, \
    AddMonsterInstanceForm, BulkAddMonsterInstanceForm, \
    BulkAddMonsterInstanceFormset, EditMonsterInstanceForm, PowerUpMonsterInstanceForm, AwakenMonsterInstanceForm, \
    MonsterPieceForm
from herders.models import Summoner, MonsterInstance, MonsterPiece, MaterialStorage, MonsterShrineStorage, ArtifactInstance
from herders.views.compare import _compare_build_objects, _compare_monster_objects

DEFAULT_VIEW_MODE = 'box'


@username_case_redirect
def monsters(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    # Determine if the person logged in is the one requesting the view
    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    monster_filter_form = FilterMonsterInstanceForm(auto_id='id_filter_%s')
    monster_filter_form.helper.form_action = reverse('herders:monster_inventory', kwargs={'profile_name': profile_name})

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'monster_filter_form': monster_filter_form,
        'view': 'profile',
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/monster_inventory/base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html')


@username_case_redirect
def monster_inventory(request, profile_name, view_mode=None, box_grouping=None):
    # If we passed in view mode or sort method, set the session variable and redirect back to ourself without the view mode or box grouping
    if view_mode:
        request.session['profile_view_mode'] = view_mode.lower()

    if box_grouping:
        request.session['profile_group_method'] = box_grouping.lower()

    if request.session.modified:
        return HttpResponse("Profile view mode cookie set")

    view_mode = request.session.get('profile_view_mode', DEFAULT_VIEW_MODE).lower()
    box_grouping = request.session.get('profile_group_method', 'grade').lower()

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    monster_queryset = MonsterInstance.objects.filter(owner=summoner).select_related(
        'monster',
        'monster__awakens_from',
        'monster__awakens_to',
    )
    total_monsters = monster_queryset.count()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if view_mode == 'list':
        monster_queryset = monster_queryset.select_related(
            'monster__leader_skill',
            'monster__awakens_to',
            'default_build',
        ).prefetch_related(
            'monster__skills',
            'default_build__runes',
            'runes',
            'artifacts',
            'team_set',
            'team_leader',
            'tags'
        )
    elif view_mode == 'collection':
        monster_queryset = monster_queryset.prefetch_related(
            'monster__skills'
        )

    form = FilterMonsterInstanceForm(request.GET or None, auto_id='id_filter_%s')
    if form.is_valid():
        monster_filter = MonsterInstanceFilter(form.cleaned_data, queryset=monster_queryset)
    else:
        monster_filter = MonsterInstanceFilter(queryset=monster_queryset)

    filtered_count = monster_filter.qs.count()

    context = {
        'monsters': monster_filter.qs,
        'total_count': total_monsters,
        'filtered_count': filtered_count,
        'profile_name': profile_name,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        if view_mode == 'pieces':
            context['monster_pieces'] = MonsterPiece.objects.filter(owner=summoner).select_related('monster')
            template = 'herders/profile/monster_inventory/summoning_pieces.html'
        elif view_mode == 'list':
            template = 'herders/profile/monster_inventory/list.html'
        elif view_mode == 'collection':
            monster_stable = {}

            # filters
            if form.is_valid():
                mon_name = form.cleaned_data['monster__name']
                filter_monster_name = (Q(name__icontains=mon_name)
                    | Q(awakens_from__name__icontains=mon_name)
                    | Q(awakens_from__awakens_from__name__icontains=mon_name)
                    | Q(awakens_to__name__icontains=mon_name))

                if form.cleaned_data['monster__natural_stars'] != "":
                    mon_stars = form.cleaned_data['monster__natural_stars'].split(',')
                    filter_nat_stars = (Q(natural_stars__gte=mon_stars[0]) & Q(natural_stars__lte=mon_stars[1]))
                else:
                    filter_nat_stars = None
            else:
                filter_monster_name = None
                filter_nat_stars = None
            
            material = (Q(archetype=Monster.ARCHETYPE_MATERIAL) | Q(archetype=Monster.ARCHETYPE_NONE))
            obtainable = Q(obtainable=True)
            unawakened = Q(awaken_level=Monster.AWAKEN_LEVEL_UNAWAKENED)

            base_material = (Q(monster__archetype=Monster.ARCHETYPE_MATERIAL) | Q(monster__archetype=Monster.ARCHETYPE_NONE))
            awakened = Q(monster__awaken_level=Monster.AWAKEN_LEVEL_AWAKENED)
            base_unawakened = Q(monster__awaken_level=Monster.AWAKEN_LEVEL_UNAWAKENED)

            base_monster_filters = obtainable & unawakened
            if filter_monster_name: 
                base_monster_filters &= filter_monster_name
            if filter_nat_stars: 
                base_monster_filters &= filter_nat_stars
            #

            base_monsters = Monster.objects.filter(base_monster_filters).exclude(material).order_by('skill_group_id', 'com2us_id').values('name', 'com2us_id', 'element', 'skill_group_id', 'skill_ups_to_max')
            devilmons_count = monster_filter.qs.filter(monster__com2us_id=61105).count()

            try:
                devilmon_material_storage = MaterialStorage.objects.select_related(
                    'item').get(owner=summoner, item__name__icontains='devilmon')
                devilmons_count += devilmon_material_storage.quantity
            except MaterialStorage.DoesNotExist:
                pass
            except MultipleObjectsReturned:
                # TODO: should be better handling for this
                pass

            skill_groups = itertools.groupby(base_monsters, lambda mon: mon['skill_group_id'])
            for skill_group_id, records in skill_groups:
                if skill_group_id == -10000:
                    continue # devilmon, somehow didn't get excluded
                records = list(records)
                data = {
                    'name': records[0]['name'],
                    'elements': {},
                    'possible_skillups': 0,
                    'devilmons_count': devilmons_count,
                }
                elements = itertools.groupby(records, lambda mon: mon['element'])
                for element, records_element in elements:
                    records_element = list(records_element)
                    data['elements'][element] = {
                        'owned': False,
                        'skilled_up': False,
                        'skill_ups_to_max': None,
                        'skillups_max': records_element[0]['skill_ups_to_max'],
                    }
                monster_stable[skill_group_id] = data

            for mon in monster_filter.qs.filter(awakened).exclude(base_material):
                mon_skill_group = monster_stable.get(mon.monster.skill_group_id)
                if not mon_skill_group:
                    continue # if skill group doesnt exist, don't care
                data = monster_stable[mon.monster.skill_group_id]['elements'].get(mon.monster.element)
                if not data:
                    continue # if base monster doesn't exist, continue (i.e. Varis)
                if data['skilled_up']:
                    continue # don't care about other units, if at least one is already fully skilled up
                if not data['owned']:
                    data['owned'] = True

                skill_ups_to_max = mon.skill_ups_to_max()
                if not skill_ups_to_max:
                    data['skilled_up'] = True
                    continue

                if not data['skill_ups_to_max'] or skill_ups_to_max < data['skill_ups_to_max']:
                    data['skill_ups_to_max'] = skill_ups_to_max

            # some other field than `monster__skill_group_id` is needed, so all records are saved, not only unique ones
            skill_up_mons = monster_filter.qs.filter(base_unawakened).exclude(base_material).values('id', 'monster__skill_group_id')
            for skill_group_id, records in itertools.groupby(skill_up_mons, lambda x: x['monster__skill_group_id']):
                monster_stable[skill_group_id]['possible_skillups'] += len(list(records))

            for mss_item in MonsterShrineStorage.objects.select_related('item').filter(owner=summoner, item__awaken_level=Monster.AWAKEN_LEVEL_UNAWAKENED):
                skill_group_id = mss_item.item.skill_group_id
                if skill_group_id in monster_stable:
                    monster_stable[skill_group_id]['possible_skillups'] += mss_item.quantity
            
            monster_stable = sorted(monster_stable.values(), key=lambda x: x['name'])
            context['monster_stable'] = monster_stable
            template = 'herders/profile/monster_inventory/collection.html'
        else:
            # Group up the filtered monsters
            monster_stable = OrderedDict()

            if box_grouping == 'grade' or box_grouping == 'stars':
                for x in reversed(range(6)):
                    monster_stable[f'{x+1}*'] = monster_filter.qs.filter(stars=x+1).order_by('-level', 'monster__element', 'monster__name')
            elif box_grouping == 'natural_stars':
                for x in reversed(range(5)):
                    monster_stable[f'Natural {x+1}*'] = monster_filter.qs.filter(monster__natural_stars=x+1).order_by('-stars', '-level', 'monster__name')
            elif box_grouping == 'level':
                monster_stable['40'] = monster_filter.qs.filter(level=40).order_by('-level', '-stars', 'monster__element', 'monster__name')
                monster_stable['39-31'] = monster_filter.qs.filter(level__gt=30).filter(level__lt=40).order_by('-level', '-stars', 'monster__element', 'monster__name')
                monster_stable['30-21'] = monster_filter.qs.filter(level__gt=20).filter(level__lte=30).order_by( '-level', '-stars', 'monster__element', 'monster__name')
                monster_stable['20-11'] = monster_filter.qs.filter(level__gt=10).filter(level__lte=20).order_by( '-level', '-stars', 'monster__element', 'monster__name')
                monster_stable['10-1'] = monster_filter.qs.filter(level__lte=10).order_by('-level', '-stars', 'monster__element', 'monster__name')
            elif box_grouping == 'element' or box_grouping == 'attribute':
                monster_stable['water'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_WATER).order_by('-stars', '-level', 'monster__name')
                monster_stable['fire'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_FIRE).order_by('-stars', '-level', 'monster__name')
                monster_stable['wind'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_WIND).order_by('-stars', '-level', 'monster__name')
                monster_stable['light'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_LIGHT).order_by('-stars', '-level', 'monster__name')
                monster_stable['dark'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_DARK).order_by('-stars', '-level', 'monster__name')
            elif box_grouping == 'archetype':
                monster_stable['attack'] = monster_filter.qs.filter(monster__archetype=Monster.ARCHETYPE_ATTACK).order_by('-stars', '-level', 'monster__name')
                monster_stable['hp'] = monster_filter.qs.filter(monster__archetype=Monster.ARCHETYPE_HP).order_by('-stars', '-level', 'monster__name')
                monster_stable['support'] = monster_filter.qs.filter(monster__archetype=Monster.ARCHETYPE_SUPPORT).order_by('-stars', '-level', 'monster__name')
                monster_stable['defense'] = monster_filter.qs.filter(monster__archetype=Monster.ARCHETYPE_DEFENSE).order_by('-stars', '-level', 'monster__name')
                monster_stable['material'] = monster_filter.qs.filter(monster__archetype=Monster.ARCHETYPE_MATERIAL).order_by('-stars', '-level', 'monster__name')
                monster_stable['other'] = monster_filter.qs.filter(monster__archetype=Monster.ARCHETYPE_NONE).order_by('-stars', '-level', 'monster__name')
            elif box_grouping == 'priority':
                monster_stable['High'] = monster_filter.qs.select_related('monster').filter(owner=summoner, priority=MonsterInstance.PRIORITY_HIGH).order_by('-level', 'monster__element', 'monster__name')
                monster_stable['Medium'] = monster_filter.qs.select_related('monster').filter(owner=summoner, priority=MonsterInstance.PRIORITY_MED).order_by('-level', 'monster__element', 'monster__name')
                monster_stable['Low'] = monster_filter.qs.select_related('monster').filter(owner=summoner, priority=MonsterInstance.PRIORITY_LOW).order_by('-level', 'monster__element', 'monster__name')
                monster_stable['None'] = monster_filter.qs.select_related('monster').filter(owner=summoner).filter(Q(priority=None) | Q(priority=0)).order_by('-level', 'monster__element', 'monster__name')
            elif box_grouping == 'family':
                for mon in monster_filter.qs:
                    family_name = mon.monster.base_monster.name

                    if family_name not in monster_stable:
                        monster_stable[family_name] = []

                    monster_stable[family_name].append(mon)

                # Sort ordered dict alphabetically by family name
                monster_stable = OrderedDict(sorted(monster_stable.items(), key=lambda family:family[0]))
            else:
                return HttpResponseBadRequest('Invalid sort method')

            context['monster_stable'] = monster_stable
            context['box_grouping'] = box_grouping.replace('_', ' ')
            template = 'herders/profile/monster_inventory/box.html'

        return render(request, template, context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
@login_required
def quick_fodder_menu(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        template = loader.get_template('herders/profile/monster_inventory/quick_fodder_menu.html')
        response_data = {
            'code': 'success',
            'html': template.render(),
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required()
def monster_instance_add(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        if request.method == 'POST':
            form = AddMonsterInstanceForm(request.POST or None)
        else:
            form = AddMonsterInstanceForm(initial=request.GET.dict())

        if request.method == 'POST' and form.is_valid():
            # Create the monster instance
            new_monster = form.save(commit=False)
            new_monster.owner = request.user.summoner
            new_monster.save()

            messages.success(request, 'Added %s to your collection.' % new_monster)

            template = loader.get_template('herders/profile/monster_inventory/monster_list_row_snippet.html')

            context = {
                'profile_name': profile_name,
                'instance': new_monster,
                'is_owner': is_owner,
            }

            response_data = {
                'code': 'success',
                'instance_id': new_monster.pk.hex,
                'html': template.render(context),
            }
        else:
            form.helper.form_action = reverse('herders:monster_instance_add', kwargs={'profile_name': profile_name})
            template = loader.get_template('herders/profile/monster_inventory/add_monster_form.html')

            # Return form filled in and errors shown
            context = {'add_monster_form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'error',
                'html': template.render(context),
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required()
def monster_instance_quick_add(request, profile_name, monster_id, stars, level):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    monster_to_add = get_object_or_404(Monster, pk=monster_id)

    if is_owner:
        new_monster = MonsterInstance.objects.create(owner=summoner, monster=monster_to_add, stars=int(stars), level=int(level), fodder=True, notes='', priority=MonsterInstance.PRIORITY_DONE)
        messages.success(request, 'Added %s to your collection.' % new_monster)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required()
def monster_instance_bulk_add(request, profile_name):
    return_path = reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    BulkAddFormset = modelformset_factory(MonsterInstance, form=BulkAddMonsterInstanceForm, formset=BulkAddMonsterInstanceFormset, extra=5, max_num=50)

    if request.method == 'POST':
        formset = BulkAddFormset(request.POST)
    else:
        formset = BulkAddFormset()

    context = {
        'profile_name': request.user.username,
        'return_path': return_path,
        'is_owner': is_owner,
        'bulk_add_formset_action': request.path + '?next=' + return_path,
        'view': 'profile',
    }

    if is_owner:
        if request.method == 'POST':
            if formset.is_valid():
                new_instances = formset.save(commit=False)
                for new_instance in new_instances:
                    try:
                        if new_instance.monster:
                            new_instance.owner = summoner

                            if new_instance.monster.archetype == Monster.ARCHETYPE_MATERIAL:
                                new_instance.priority = MonsterInstance.PRIORITY_DONE

                            new_instance.save()
                            messages.success(request, 'Added %s to your collection.' % new_instance)
                    except ObjectDoesNotExist:
                        # Blank form, don't care
                        pass

                return redirect(return_path)
    else:
        raise PermissionDenied("Trying to bulk add to profile you don't own")

    context['bulk_add_formset'] = formset
    return render(request, 'herders/profile/monster_inventory/bulk_add_form.html', context)


@username_case_redirect
def monster_instance_view(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        request.path
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'return_path': return_path,
        'is_owner': is_owner,
        'view': 'profile',
    }

    try:
        context['instance'] = MonsterInstance.objects.select_related('monster', 'monster__leader_skill').prefetch_related('monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        return render(request, 'herders/profile/monster_view/not_found.html', context)

    if is_owner or summoner.public:
        return render(request, 'herders/profile/monster_view/base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html')


@username_case_redirect
def monster_instance_view_runes(request, profile_name, instance_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    try:
        instance = MonsterInstance.objects.select_related(
            'monster', 'monster__leader_skill', 'default_build'
        ).prefetch_related(
            'monster__skills', 'default_build__runes', 'default_build__artifacts', 
        ).get(pk=instance_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

    # Get all slotted runes and artifacts, with None in place of empty slots
    runes = [instance.default_build.runes.filter(slot=slot + 1).first() for slot in range(6)]
    artifacts = {
        desc.lower(): instance.default_build.artifacts.filter(slot=slot).first()
        for slot, desc in ArtifactInstance.SLOT_CHOICES
    }

    context = {
        'runes': runes,
        'artifacts': artifacts,
        'instance': instance,
        'profile_name': profile_name,
        'is_owner': is_owner,
    }

    return render(request, 'herders/profile/monster_view/runes.html', context)


@username_case_redirect
def monster_instance_view_stats(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.objects.select_related('monster', 'default_build').get(pk=instance_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

    context = {
        'instance': instance,
        'max_stats': instance.get_max_level_stats(),
        'bldg_stats': instance.get_building_stats(),
        'guild_stats': instance.get_building_stats(Building.AREA_GUILD),
    }

    return render(request, 'herders/profile/monster_view/stats.html', context)


@username_case_redirect
def monster_instance_view_skills(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.objects.select_related('monster', 'monster__leader_skill').prefetch_related('monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

    # Reconcile skill level with actual skill from base monster
    skills = []
    skill_levels = [
        instance.skill_1_level,
        instance.skill_2_level,
        instance.skill_3_level,
        instance.skill_4_level,
    ]

    for idx in range(0, instance.monster.skills.count()):
        skills.append({
            'skill': instance.monster.skills.all()[idx],
            'level': skill_levels[idx]
        })

    context = {
        'instance': instance,
        'skills': skills,
    }

    return render(request, 'herders/profile/monster_view/skills.html', context)


@username_case_redirect
def monster_instance_view_info(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.objects.select_related('monster', 'monster__leader_skill').prefetch_related('monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

    if instance.monster.awaken_level == Monster.AWAKEN_LEVEL_INCOMPLETE:
        ingredient_in = Fusion.objects.filter(ingredients__awakens_from__awakens_from__pk=instance.monster.pk)
        product_of_query = 'product__pk'
    elif instance.monster.awaken_level == Monster.AWAKEN_LEVEL_UNAWAKENED:
        ingredient_in = Fusion.objects.filter(ingredients__awakens_from__pk=instance.monster.pk)
        product_of_query = 'product__pk'
    elif instance.monster.awaken_level == Monster.AWAKEN_LEVEL_AWAKENED:
        ingredient_in = Fusion.objects.filter(ingredients__pk=instance.monster.pk)
        product_of_query = 'product__awakens_to__pk'
    elif instance.monster.awaken_level == Monster.AWAKEN_LEVEL_SECOND:
        ingredient_in = Fusion.objects.filter(ingredients__awakens_to__pk=instance.monster.pk)
        product_of_query = 'product__awakens_to__awakens_to__pk'
    else:
        ingredient_in = None
        product_of_query = 'product__pk'

    product_of = Fusion.objects.filter(**{product_of_query: instance.monster.pk}).first()

    context = {
        'instance': instance,
        'profile_name': profile_name,
        'fusion_ingredient_in': ingredient_in,
        'fusion_product_of': product_of,
        'skillups': instance.get_possible_skillups(),
    }

    return render(request, 'herders/profile/monster_view/notes_info.html', context)


@username_case_redirect
@login_required()
def monster_instance_remove_runes(request, profile_name, instance_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        try:
            instance = MonsterInstance.objects.select_related(
                'default_build',
            ).prefetch_related(
                'runes'
            ).get(pk=instance_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()
        else:
            instance.default_build.runes.clear()
            messages.success(request, 'Removed all runes from ' + str(instance))
            response_data = {
                'code': 'success',
            }
            return JsonResponse(response_data)
    else:
        raise PermissionDenied()


@username_case_redirect
@login_required()
def monster_instance_edit(request, profile_name, instance_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    instance = get_object_or_404(MonsterInstance, pk=instance_id)
    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        # Reconcile skill level with actual skill from base monster
        skills = []
        skill_levels = [
            instance.skill_1_level,
            instance.skill_2_level,
            instance.skill_3_level,
            instance.skill_4_level,
        ]

        for idx in range(0, instance.monster.skills.count()):
            skills.append({
                'skill': instance.monster.skills.all()[idx],
                'level': skill_levels[idx]
            })

        form = EditMonsterInstanceForm(request.POST or None, instance=instance)
        form.helper.form_action = request.path
        if len(skills) >= 1 and skills[0]['skill'].max_level > 1:
            form.helper['skill_1_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_1", data_skill_field=form['skill_1_level'].auto_id),
            )
            form.helper['skill_1_level'].wrap(Field, min=1, max=skills[0]['skill'].max_level)
            form.fields['skill_1_level'].label = skills[0]['skill'].name + " Level"
        else:
            form.helper['skill_1_level'].wrap(Div, css_class="hidden")

        if len(skills) >= 2 and skills[1]['skill'].max_level > 1:
            form.helper['skill_2_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_2", data_skill_field=form['skill_2_level'].auto_id),
                min=1,
                max=skills[1]['skill'].max_level,
            )
            form.helper['skill_2_level'].wrap(Field, min=1, max=skills[1]['skill'].max_level)
            form.fields['skill_2_level'].label = skills[1]['skill'].name + " Level"
        else:
            form.helper['skill_2_level'].wrap(Div, css_class="hidden")

        if len(skills) >= 3 and skills[2]['skill'].max_level > 1:
            form.helper['skill_3_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_3", data_skill_field=form['skill_3_level'].auto_id),
                min=1,
                max=skills[2]['skill'].max_level,
            )
            form.helper['skill_3_level'].wrap(Field, min=1, max=skills[2]['skill'].max_level)
            form.fields['skill_3_level'].label = skills[2]['skill'].name + " Level"
        else:
            form.helper['skill_3_level'].wrap(Div, css_class="hidden")

        if len(skills) >= 4 and skills[3]['skill'].max_level > 1:
            form.helper['skill_4_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_4", data_skill_field=form['skill_4_level'].auto_id),
                min=1,
                max=skills[1]['skill'].max_level,
            )
            form.helper['skill_4_level'].wrap(Field, min=1, max=skills[3]['skill'].max_level)
            form.fields['skill_4_level'].label = skills[3]['skill'].name + " Level"
        else:
            form.helper['skill_4_level'].wrap(Div, css_class="hidden")

        if not instance.monster.homunculus:
            form.helper['custom_name'].wrap(Div, css_class="hidden")

        if request.method == 'POST' and form.is_valid():
            mon = form.save()
            messages.success(request, 'Successfully edited ' + str(mon))

            view_mode = request.session.get('profile_view_mode', DEFAULT_VIEW_MODE).lower()

            if view_mode == 'list':
                template = loader.get_template('herders/profile/monster_inventory/monster_list_row_snippet.html')
            else:
                template = loader.get_template('herders/profile/monster_inventory/monster_box_snippet.html')

            context = {
                'profile_name': profile_name,
                'instance': mon,
                'is_owner': is_owner,
            }

            response_data = {
                'code': 'success',
                'instance_id': mon.pk.hex,
                'html': template.render(context),
            }
        else:
            # Return form filled in and errors shown
            template = loader.get_template('herders/profile/monster_view/edit_form.html')
            context = {'edit_monster_form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'error',
                'html': template.render(context)
            }

        return JsonResponse(response_data)
    else:
        raise PermissionDenied()


@username_case_redirect
@login_required()
def monster_instance_delete(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    # Check for proper owner before deleting
    if request.user.summoner == monster.owner:
        messages.warning(request, 'Deleted ' + str(monster))
        monster.delete()

        return redirect(return_path)
    else:
        return HttpResponseBadRequest()


@username_case_redirect
@login_required()
def monster_instance_power_up(request, profile_name, instance_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    form = PowerUpMonsterInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:monster_instance_power_up', kwargs={'profile_name': profile_name, 'instance_id': instance_id})

    context = {
        'profile_name': request.user.username,
        'monster': monster,
        'is_owner': is_owner,
        'form': form,
        'view': 'profile',
    }

    validation_errors = {}
    response_data = {
        'code': 'error'
    }

    if is_owner:
        if request.method == 'POST' and form.is_valid():
            food_monsters = form.cleaned_data['monster']

            # Check that monster is not being fed to itself
            if monster in food_monsters:
                validation_errors['base_food_same'] = "You can't feed a monster to itself. "

            is_evolution = request.POST.get('evolve', False)

            # Perform validation checks for evolve action
            if is_evolution:
                # Check constraints on evolving (or not, if form element was set)
                # Check monster level and stars
                if monster.stars >= 6:
                    validation_errors['base_monster_stars'] = "%s is already at 6 stars." % monster.monster.name

                if not form.cleaned_data['ignore_evolution']:
                    if monster.level != monster.max_level_from_stars():
                        validation_errors['base_monster_level'] = "%s is not at max level for the current star rating (Lvl %s)." % (monster.monster.name, monster.monster.max_level_from_stars())

                    # Check number of fodder monsters
                    if len(food_monsters) < monster.stars:
                        validation_errors['food_monster_quantity'] = "Evolution requres %s food monsters." % monster.stars

                    # Check fodder star ratings - must be same as monster
                    for food in food_monsters:
                        if food.stars != monster.stars:
                            if 'food_monster_stars' not in validation_errors:
                                validation_errors['food_monster_stars'] = "All food monsters must be %s stars or higher." % monster.stars

                # Perform the stars++ if no errors
                if not validation_errors:
                    # Level up stars
                    monster.stars += 1
                    monster.level = 1
                    monster.save()
                    messages.success(request, 'Successfully evolved %s to %s<span class="glyphicon glyphicon-star"></span>' % (monster.monster.name, monster.stars), extra_tags='safe')

            if not validation_errors:
                # Delete the submitted monsters
                for food in food_monsters:
                    if food.owner == request.user.summoner:
                        messages.warning(request, 'Deleted %s' % food)
                        food.delete()
                    else:
                        raise PermissionDenied("Trying to delete a monster you don't own")

                # Redirect back to return path if evolved, or go to edit screen if power up
                if is_evolution:
                    response_data['code'] = 'success'
                else:
                    response_data['code'] = 'edit'

                return JsonResponse(response_data)
    else:
        raise PermissionDenied("Trying to power up or evolve a monster you don't own")

    template = loader.get_template('herders/profile/monster_view/power_up_form.html')
    # Any errors in the form will fall through to here and be displayed
    context['validation_errors'] = validation_errors
    context.update(csrf(request))
    response_data['html'] = template.render(context)

    return JsonResponse(response_data)


@username_case_redirect
@login_required()
def monster_instance_awaken(request, profile_name, instance_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    template = loader.get_template('herders/profile/monster_view/awaken_form.html')

    form = AwakenMonsterInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:monster_instance_awaken', kwargs={'profile_name': profile_name, 'instance_id': instance_id})

    if is_owner:
        if monster.monster.awakens_to is not None:
            if monster.monster.awakens_to.awaken_level == Monster.AWAKEN_LEVEL_SECOND:
                # Just do it without messing with essence storage
                monster.monster = monster.monster.awakens_to
                monster.save()

                response_data = {
                    'code': 'success',
                    'removeElement': '#awakenMonsterButton',
                }
            else:
                monster_awakening_materials = monster.monster.get_awakening_materials()
                summoner_material_storage = {ms.item.com2us_id: ms for ms in MaterialStorage.objects.select_related('item').filter(owner=summoner)}

                # Display form confirming essences subtracted
                if request.method == 'POST' and form.is_valid():
                    # Subtract essences from inventory if requested
                    if form.cleaned_data['subtract_materials']:
                        summoner = Summoner.objects.get(user=request.user)

                        # bulk_update doesn't use `save()` method inside Model, so we need to take care of negative numbers
                        material_storage_edited = []
                        material_storage_created = []
                        for element, essences in monster_awakening_materials.items():
                            for essence, needed in essences.items():
                                if needed > 0:
                                    if ESSENCE_MAP[element][essence] not in summoner_material_storage:
                                        material_storage_created.append(MaterialStorage(
                                            owner=summoner,
                                            quantity=0,
                                            item=GameItem.objects.get(com2us_id=ESSENCE_MAP[element][essence], category=GameItem.CATEGORY_ESSENCE)
                                        ))
                                        continue
                                    material_storage_edited.append(summoner_material_storage[ESSENCE_MAP[element][essence]])
                                    material_storage_edited[-1].quantity = max(material_storage_edited[-1].quantity - needed, 0)
                        MaterialStorage.objects.bulk_create(material_storage_created)
                        MaterialStorage.objects.bulk_update(material_storage_edited, ['quantity'])
                    # Perform the awakening by instance's monster source ID
                    monster.monster = monster.monster.awakens_to
                    monster.save()

                    response_data = {
                        'code': 'success',
                        'removeElement': '#awakenMonsterButton',
                    }
                else:
                    available_essences = OrderedDict()

                    for element, essences in monster_awakening_materials.items():
                        available_essences[element] = OrderedDict()
                        for size, cost in essences.items():
                            if cost > 0:
                                qty = summoner_material_storage[ESSENCE_MAP[element][size]].quantity if ESSENCE_MAP[element][size] in summoner_material_storage else 0
                                available_essences[element][size] = {
                                    'qty': qty,
                                    'sufficient': qty >= cost,
                                }

                    context = {
                        'code': 'confirm',
                        'awaken_form': form,
                        'available_essences': available_essences,
                        'instance': monster,
                    }
                    context.update(csrf(request))

                    response_data = {
                        'code': 'error',
                        'html': template.render(context)
                    }
        else:
            error_template = loader.get_template('herders/profile/monster_already_awakened.html')
            response_data = {
                'code': 'error',
                'html': error_template.render()
            }

        return JsonResponse(response_data)
    else:
        raise PermissionDenied()


@username_case_redirect
@login_required()
def monster_instance_duplicate(request, profile_name, instance_id):
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    # Check for proper owner before copying
    if request.user.summoner == monster.owner:
        newmonster = monster
        newmonster.pk = None
        newmonster.save()
        messages.success(request, 'Succesfully copied ' + str(newmonster))

        view_mode = request.session.get('profile_view_mode', DEFAULT_VIEW_MODE).lower()

        if view_mode == 'list':
            template = loader.get_template('herders/profile/monster_inventory/monster_list_row_snippet.html')
        else:
            template = loader.get_template('herders/profile/monster_inventory/monster_box_snippet.html')

        context = {
            'profile_name': profile_name,
            'is_owner': True,
            'instance': newmonster,
        }

        response_data = {
            'code': 'success',
            'instance_id': newmonster.pk.hex,
            'html': template.render(context),
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required()
def monster_piece_add(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        if request.method == 'POST':
            form = MonsterPieceForm(request.POST or None)
        else:
            form = MonsterPieceForm()

        form.helper.form_action = reverse('herders:monster_piece_add', kwargs={'profile_name': profile_name})

        template = loader.get_template('herders/profile/monster_inventory/monster_piece_form.html')

        if request.method == 'POST' and form.is_valid():
            # Create the monster instance
            new_pieces = form.save(commit=False)
            new_pieces.owner = request.user.summoner
            new_pieces.save()

            messages.success(request, 'Added %s to your collection.' % new_pieces)

            response_data = {
                'code': 'success'
            }
        else:
            # Return form filled in and errors shown
            context = {'form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'error',
                'html': template.render(context),
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required()
def monster_piece_edit(request, profile_name, instance_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    pieces = get_object_or_404(MonsterPiece, pk=instance_id)
    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    template = loader.get_template('herders/profile/monster_inventory/monster_piece_form.html')

    if is_owner:
        form = MonsterPieceForm(request.POST or None, instance=pieces)
        form.helper.form_action = request.path

        if request.method == 'POST' and form.is_valid():
            new_piece = form.save()
            template = loader.get_template('herders/profile/monster_inventory/monster_piece_snippet.html')

            context = {
                'piece': new_piece,
                'is_owner': is_owner,
            }

            # Delete if 0
            if new_piece.pieces <= 0:
                new_piece.delete()
                response_data = {
                    'code': 'success',
                }
            else:
                response_data = {
                    'code': 'success',
                    'instance_id': new_piece.pk.hex,
                    'html': template.render(context),
                }
        else:
            # Return form filled in and errors shown
            context = {'form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'error',
                'html': template.render(context),
            }

        return JsonResponse(response_data)
    else:
        raise PermissionDenied()


@username_case_redirect
@login_required()
def monster_piece_summon(request, profile_name, instance_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    pieces = get_object_or_404(MonsterPiece, pk=instance_id)
    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        if pieces.can_summon():
            new_monster = MonsterInstance.objects.create(owner=summoner, monster=pieces.monster, stars=pieces.monster.natural_stars, level=1, fodder=False, notes='', priority=MonsterInstance.PRIORITY_DONE)
            messages.success(request, 'Added %s to your collection.' % new_monster)

            # Remove the pieces, delete if 0
            pieces.pieces -= pieces.PIECE_REQUIREMENTS[pieces.monster.natural_stars]
            pieces.save()

            response_data = {
                'code': 'success',
            }

            if pieces.pieces <= 0:
                pieces.delete()
            else:
                template = loader.get_template('herders/profile/monster_inventory/monster_piece_snippet.html')
                context = {
                    'piece': pieces,
                    'is_owner': is_owner,
                }
                response_data['instance_id'] = pieces.pk.hex
                response_data['html'] = template.render(context),

            return JsonResponse(response_data)
    else:
        raise PermissionDenied()


@username_case_redirect
@login_required()
def monster_piece_delete(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    pieces = get_object_or_404(MonsterPiece, pk=instance_id)

    # Check for proper owner before deleting
    if request.user.summoner == pieces.owner:
        messages.warning(request, 'Deleted ' + str(pieces))
        pieces.delete()

        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def monster_compare(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = CompareMonstersForm(request.POST)
        
        if form.is_valid():
            context = {
                'is_owner': is_owner,
                'profile_name': profile_name,
                'form': form,
                "monsters": [form.cleaned_data['monster_first'], form.cleaned_data['monster_second']],
                'comparison': {
                    'builds': _compare_build_objects(form.cleaned_data['monster_first'], form.cleaned_data['monster_second']),
                    'monsters': _compare_monster_objects(form.cleaned_data['monster_first'], form.cleaned_data['monster_second']),
                    'rta_builds': _compare_build_objects(form.cleaned_data['monster_first'], form.cleaned_data['monster_second'], rta=True),
                },
                'view': 'profile',
            }
            return render(request, 'herders/profile/monster_inventory/compare.html', context)
        else:
            return HttpResponseBadRequest()
    else:
        context = {
            'is_owner': is_owner,
            'profile_name': profile_name,
            'form': CompareMonstersForm(),
            'view': 'profile',
        }

        return render(request, 'herders/profile/monster_inventory/compare.html', context)
