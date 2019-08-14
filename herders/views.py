import json
from collections import OrderedDict
from copy import deepcopy
from functools import reduce

from celery.result import AsyncResult
from crispy_forms.bootstrap import FieldWithButtons, StrictButton, Field, Div
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.mail import mail_admins
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.db.models import FieldDoesNotExist, Q
from django.forms.models import modelformset_factory
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader
from django.template.context_processors import csrf
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from bestiary.models import Monster, Fusion, Building
from .decorators import username_case_redirect
from .filters import MonsterInstanceFilter, RuneInstanceFilter
from .forms import RegisterUserForm, CrispyChangeUsernameForm, DeleteProfileForm, FilterMonsterInstanceForm, \
    EditBuildingForm, EditUserForm, EditSummonerForm, AddMonsterInstanceForm, BulkAddMonsterInstanceForm, \
    BulkAddMonsterInstanceFormset, EditMonsterInstanceForm, PowerUpMonsterInstanceForm, AwakenMonsterInstanceForm, \
    MonsterPieceForm, AddTeamGroupForm, EditTeamGroupForm, DeleteTeamGroupForm, EditTeamForm, FilterRuneForm, \
    AddRuneInstanceForm, AssignRuneForm, AddRuneCraftInstanceForm, ImportPCAPForm, ImportSWParserJSONForm, \
    FilterLogTimeRangeMixin, FilterDungeonLogForm
from .models import Summoner, BuildingInstance, MonsterInstance, MonsterPiece, TeamGroup, Team, RuneInstance, \
    RuneCraftInstance, Storage
from .profile_parser import parse_pcap, validate_sw_json
from .rune_optimizer_parser import export_win10
from .tasks import com2us_data_import

DEFAULT_VIEW_MODE = 'box'

DEFAULT_IMPORT_OPTIONS = {
    'clear_profile': False,
    'default_priority': '',
    'lock_monsters': True,
    'minimum_stars': 1,
    'ignore_silver': False,
    'ignore_material': False,
    'except_with_runes': True,
    'except_light_and_dark': True,
    'except_fusion_ingredient': True,
    'delete_missing_monsters': 1,
    'delete_missing_runes': 1,
    'ignore_validation_errors': False
}


def register(request):
    form = RegisterUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            if User.objects.filter(username__iexact=form.cleaned_data['username']).exists():
                form.add_error('username', 'Username already taken')
            else:
                new_user = None
                new_summoner = None

                try:
                    # Create the user
                    new_user = User.objects.create_user(
                        username=form.cleaned_data['username'],
                        password=form.cleaned_data['password'],
                        email=form.cleaned_data['email'],
                    )
                    new_user.save()
                    new_user.groups.add(Group.objects.get(name='Summoners'))
                    new_summoner = Summoner.objects.create(
                        user=new_user,
                        summoner_name=form.cleaned_data['summoner_name'],
                        public=form.cleaned_data['is_public'],
                    )
                    new_summoner.save()

                    # Automatically log them in
                    user = authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            return redirect('herders:profile_default', profile_name=user.username)
                except IntegrityError as e:
                    if new_user is not None:
                        new_user.delete()
                    if new_summoner is not None:
                        new_summoner.delete()

                    form.add_error(None, 'There was an issue completing your registration. Please try again.')
                    mail_admins(
                        subject='Error during user registration',
                        message='{}'.format(e),
                        fail_silently=True,
                    )

    context = {'form': form}

    return render(request, 'herders/register.html', context)


@login_required
def change_username(request):
    user = request.user
    form = CrispyChangeUsernameForm(request.POST or None)

    context = {
        'form': form,
    }

    if request.method == 'POST' and form.is_valid():
        try:
            user.username = form.cleaned_data['username']
            user.save()

            return redirect('username_change_complete')
        except IntegrityError:
            form.add_error('username', 'Username already taken')

    return render(request, 'registration/change_username.html', context)


def change_username_complete(request):
    return render(request, 'registration/change_username_complete.html')


@username_case_redirect
@login_required
def profile_delete(request, profile_name):
    user = request.user
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    form = DeleteProfileForm(request.POST or None)
    form.helper.form_action = reverse('herders:profile_delete', kwargs={'profile_name': profile_name})

    context = {
        'form': form,
    }
    if is_owner:
        if request.method == 'POST' and form.is_valid():
            logout(request)
            user.delete()
            messages.warning(request, 'Your profile has been permanently deleted.')
            return redirect('news:latest_news')

        return render(request, 'herders/profile/profile_delete.html', context)
    else:
        return HttpResponseForbidden("You don't own this profile")


@username_case_redirect
@login_required
def following(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_following', kwargs={'profile_name': profile_name})
    )

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'summoner': summoner,
        'view': 'following',
        'return_path': return_path,
    }

    return render(request, 'herders/profile/following/list.html', context)


@username_case_redirect
@login_required
def follow_add(request, profile_name, follow_username):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    new_follower = get_object_or_404(Summoner, user__username=follow_username)
    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        summoner.following.add(new_follower)
        messages.info(request, 'Now following %s' % new_follower.user.username)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def follow_remove(request, profile_name, follow_username):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    removed_follower = get_object_or_404(Summoner, user__username=follow_username)
    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        summoner.following.remove(removed_follower)
        messages.info(request, 'Unfollowed %s' % removed_follower.user.username)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@username_case_redirect
def profile(request, profile_name):
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
def buildings(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    context = {
        'summoner': summoner,
        'is_owner': is_owner,
        'profile_name': profile_name,
    }

    return render(request, 'herders/profile/buildings/base.html', context)


@username_case_redirect
def buildings_inventory(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    all_buildings = Building.objects.all().order_by('name')

    building_data = []
    total_glory_cost = 0
    spent_glory = 0
    total_guild_cost = 0
    spent_guild = 0

    for b in all_buildings:
        bldg_data = _building_data(summoner, b)
        if b.area == Building.AREA_GENERAL:
            total_glory_cost += sum(b.upgrade_cost)
            spent_glory += bldg_data['spent_upgrade_cost']
        elif b.area == Building.AREA_GUILD:
            total_guild_cost += sum(b.upgrade_cost)
            spent_guild += bldg_data['spent_upgrade_cost']

        building_data.append(bldg_data)

    context = {
        'is_owner': is_owner,
        'summoner': summoner,
        'profile_name': profile_name,
        'buildings': building_data,
        'total_glory_cost': total_glory_cost,
        'spent_glory': spent_glory,
        'glory_progress': float(spent_glory) / total_glory_cost * 100,
        'total_guild_cost': total_guild_cost,
        'spent_guild': spent_guild,
        'guild_progress': float(spent_guild) / total_guild_cost * 100,
    }

    return render(request, 'herders/profile/buildings/inventory.html', context)


@username_case_redirect
@login_required
def building_edit(request, profile_name, building_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    base_building = get_object_or_404(Building, pk=building_id)

    try:
        owned_instance = BuildingInstance.objects.get(owner=summoner, building=base_building)
    except BuildingInstance.DoesNotExist:
        owned_instance = BuildingInstance.objects.create(owner=summoner, level=0, building=base_building)

    form = EditBuildingForm(request.POST or None, instance=owned_instance)
    form.helper.form_action = reverse('herders:building_edit', kwargs={'profile_name': profile_name, 'building_id': building_id})

    context = {
        'form': form,
    }
    context.update(csrf(request))

    if is_owner:
        if request.method == 'POST' and form.is_valid():
            owned_instance = form.save()
            messages.success(request,'Updated ' + owned_instance.building.name + ' to level ' + str(owned_instance.level))

            response_data = {
                'code': 'success',
            }
        else:
            template = loader.get_template('herders/profile/buildings/edit_form.html')
            response_data = {
                'code': 'error',
                'html': template.render(context),
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


def _building_data(summoner, building):
    percent_stat = building.affected_stat in Building.PERCENT_STATS
    total_upgrade_cost = sum(building.upgrade_cost)
    if building.area == Building.AREA_GENERAL:
        currency = 'glory_points.png'
    else:
        currency = 'guild_points.png'

    try:
        instance = BuildingInstance.objects.get(owner=summoner, building=building)
        if instance.level > 0:
            stat_bonus = building.stat_bonus[instance.level - 1]
        else:
            stat_bonus = 0

        remaining_upgrade_cost = instance.remaining_upgrade_cost()
    except BuildingInstance.DoesNotExist:
        instance = None
        stat_bonus = 0
        remaining_upgrade_cost = total_upgrade_cost
    except BuildingInstance.MultipleObjectsReturned:
        # Should only be 1 ever - use the first and delete the others.
        instance = BuildingInstance.objects.filter(owner=summoner, building=building).first()
        BuildingInstance.objects.filter(owner=summoner, building=building).exclude(pk=instance.pk).delete()
        return _building_data(summoner, building)

    return {
        'base': building,
        'instance': instance,
        'stat_bonus': stat_bonus,
        'percent_stat': percent_stat,
        'spent_upgrade_cost': total_upgrade_cost - remaining_upgrade_cost,
        'total_upgrade_cost': total_upgrade_cost,
        'upgrade_progress': float(total_upgrade_cost - remaining_upgrade_cost) / total_upgrade_cost * 100,
        'currency': currency,
    }


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

    monster_queryset = MonsterInstance.objects.filter(owner=summoner).select_related('monster', 'monster__awakens_from')
    total_monsters = monster_queryset.count()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if view_mode == 'list':
        monster_queryset = monster_queryset.select_related(
            'monster__leader_skill', 'monster__awakens_to'
        ).prefetch_related(
            'monster__skills', 'runeinstance_set', 'team_set', 'team_leader', 'tags'
        )

    form = FilterMonsterInstanceForm(request.POST or None, auto_id='id_filter_%s')
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
                monster_stable['attack'] = monster_filter.qs.filter(monster__archetype=Monster.TYPE_ATTACK).order_by('-stars', '-level', 'monster__name')
                monster_stable['hp'] = monster_filter.qs.filter(monster__archetype=Monster.TYPE_HP).order_by('-stars', '-level', 'monster__name')
                monster_stable['support'] = monster_filter.qs.filter(monster__archetype=Monster.TYPE_SUPPORT).order_by('-stars', '-level', 'monster__name')
                monster_stable['defense'] = monster_filter.qs.filter(monster__archetype=Monster.TYPE_DEFENSE).order_by('-stars', '-level', 'monster__name')
                monster_stable['material'] = monster_filter.qs.filter(monster__archetype=Monster.TYPE_MATERIAL).order_by('-stars', '-level', 'monster__name')
                monster_stable['other'] = monster_filter.qs.filter(monster__archetype=Monster.TYPE_NONE).order_by('-stars', '-level', 'monster__name')
            elif box_grouping == 'priority':
                monster_stable['High'] = monster_filter.qs.select_related('monster').filter(owner=summoner, priority=MonsterInstance.PRIORITY_HIGH).order_by('-level', 'monster__element', 'monster__name')
                monster_stable['Medium'] = monster_filter.qs.select_related('monster').filter(owner=summoner, priority=MonsterInstance.PRIORITY_MED).order_by('-level', 'monster__element', 'monster__name')
                monster_stable['Low'] = monster_filter.qs.select_related('monster').filter(owner=summoner, priority=MonsterInstance.PRIORITY_LOW).order_by('-level', 'monster__element', 'monster__name')
                monster_stable['None'] = monster_filter.qs.select_related('monster').filter(owner=summoner).filter(Q(priority=None) | Q(priority=0)).order_by('-level', 'monster__element', 'monster__name')
            elif box_grouping == 'family':
                for mon in monster_filter.qs:
                    if mon.monster.is_awakened and mon.monster.awakens_from is not None:
                        family_name = mon.monster.awakens_from.name
                    else:
                        family_name = mon.monster.name

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
def profile_edit(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    user_form = EditUserForm(request.POST or None, instance=request.user)
    summoner_form = EditSummonerForm(request.POST or None, instance=request.user.summoner)

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'summoner': summoner,
        'return_path': return_path,
        'user_form': user_form,
        'summoner_form': summoner_form,
    }

    if is_owner:
        if request.method == 'POST' and summoner_form.is_valid() and user_form.is_valid():
            summoner_form.save()
            user_form.save()

            messages.info(request, 'Your profile has been updated.')
            return redirect(return_path)
        else:
            return render(request, 'herders/profile/profile_edit.html', context)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def storage(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        craft_mats = []
        essence_mats = []
        monster_mats = []

        for field_name in Storage.ESSENCE_FIELDS:
            essence_mats.append({
                'name': summoner.storage._meta.get_field(field_name).help_text,
                'field_name': field_name,
                'element': field_name.split('_')[0],
                'qty': getattr(summoner.storage, field_name)
            })

        for field_name in Storage.CRAFT_FIELDS:
            craft_mats.append({
                'name': summoner.storage._meta.get_field(field_name).help_text,
                'field_name': field_name,
                'qty': getattr(summoner.storage, field_name)
            })

        for field_name in Storage.MONSTER_FIELDS:
            monster_mats.append({
                'name': summoner.storage._meta.get_field(field_name).help_text,
                'field_name': field_name if not field_name.startswith('rainbowmon') else 'rainbowmon',
                'qty': getattr(summoner.storage, field_name)
            })

        context = {
            'is_owner': is_owner,
            'profile_name': profile_name,
            'summoner': summoner,
            'essence_mats': essence_mats,
            'craft_mats': craft_mats,
            'monster_mats': monster_mats,
        }

        return render(request, 'herders/profile/storage/base.html', context=context)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def storage_update(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner and request.POST:
        field_name = request.POST.get('name')
        try:
            new_value = int(request.POST.get('value'))
        except ValueError:
            return HttpResponseBadRequest('Invalid Entry')

        essence_size = None

        if 'essence' in field_name:
            # Split the actual field name off from the size
            try:
                field_name, essence_size = field_name.split('.')
                size_map = {
                    'low': Storage.ESSENCE_LOW,
                    'mid': Storage.ESSENCE_MID,
                    'high': Storage.ESSENCE_HIGH,
                }
                essence_size = size_map[essence_size]
            except (ValueError, KeyError):
                return HttpResponseBadRequest()

        try:
            Storage._meta.get_field(field_name)
        except FieldDoesNotExist:
            return HttpResponseBadRequest()
        else:
            if essence_size is not None:
                # Get a copy of the size array and set the correct index to new value
                essence_list = getattr(summoner.storage, field_name)
                essence_list[essence_size] = new_value
                new_value = essence_list

            setattr(summoner.storage, field_name, new_value)
            summoner.storage.save()
            return HttpResponse()
    else:
        return HttpResponseForbidden()


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

                            if new_instance.monster.archetype == Monster.TYPE_MATERIAL:
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
        instance = MonsterInstance.objects.select_related('monster', 'monster__leader_skill').prefetch_related('monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        return HttpResponseBadRequest()

    instance_runes = [
        instance.runeinstance_set.filter(slot=1).first(),
        instance.runeinstance_set.filter(slot=2).first(),
        instance.runeinstance_set.filter(slot=3).first(),
        instance.runeinstance_set.filter(slot=4).first(),
        instance.runeinstance_set.filter(slot=5).first(),
        instance.runeinstance_set.filter(slot=6).first(),
    ]

    context = {
        'runes': instance_runes,
        'instance': instance,
        'profile_name': profile_name,
        'is_owner': is_owner,
    }

    return render(request, 'herders/profile/monster_view/runes.html', context)


@username_case_redirect
def monster_instance_view_stats(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.objects.select_related('monster').get(pk=instance_id)
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

    if instance.monster.is_awakened:
        ingredient_in = instance.monster.fusion_set.all()
    elif instance.monster.can_awaken and instance.monster.awakens_to:
        ingredient_in = instance.monster.awakens_to.fusion_set.all()
    else:
        ingredient_in = []

    if instance.monster.is_awakened and instance.monster.awakens_from:
        product_of = instance.monster.awakens_from.product.first()
    elif instance.monster.can_awaken:
        product_of = instance.monster.product.first()
    else:
        product_of = []

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
            instance = MonsterInstance.objects.get(pk=instance_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest()
        else:
            for rune in instance.runeinstance_set.all():
                rune.assigned_to = None
                rune.save()

            instance.save()
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
        if not monster.monster.is_awakened:
            if request.method == 'POST' and form.is_valid():
                # Subtract essences from inventory if requested
                if form.cleaned_data['subtract_materials']:
                    summoner = Summoner.objects.get(user=request.user)

                    summoner.storage.magic_essence[Storage.ESSENCE_HIGH] -= monster.monster.awaken_mats_magic_high
                    summoner.storage.magic_essence[Storage.ESSENCE_MID] -= monster.monster.awaken_mats_magic_mid
                    summoner.storage.magic_essence[Storage.ESSENCE_LOW] -= monster.monster.awaken_mats_magic_low
                    summoner.storage.fire_essence[Storage.ESSENCE_HIGH] -= monster.monster.awaken_mats_fire_high
                    summoner.storage.fire_essence[Storage.ESSENCE_MID] -= monster.monster.awaken_mats_fire_mid
                    summoner.storage.fire_essence[Storage.ESSENCE_LOW] -= monster.monster.awaken_mats_fire_low
                    summoner.storage.water_essence[Storage.ESSENCE_HIGH] -= monster.monster.awaken_mats_water_high
                    summoner.storage.water_essence[Storage.ESSENCE_MID] -= monster.monster.awaken_mats_water_mid
                    summoner.storage.water_essence[Storage.ESSENCE_LOW] -= monster.monster.awaken_mats_water_low
                    summoner.storage.wind_essence[Storage.ESSENCE_HIGH] -= monster.monster.awaken_mats_wind_high
                    summoner.storage.wind_essence[Storage.ESSENCE_MID] -= monster.monster.awaken_mats_wind_mid
                    summoner.storage.wind_essence[Storage.ESSENCE_LOW] -= monster.monster.awaken_mats_wind_low
                    summoner.storage.dark_essence[Storage.ESSENCE_HIGH] -= monster.monster.awaken_mats_dark_high
                    summoner.storage.dark_essence[Storage.ESSENCE_MID] -= monster.monster.awaken_mats_dark_mid
                    summoner.storage.dark_essence[Storage.ESSENCE_LOW] -= monster.monster.awaken_mats_dark_low
                    summoner.storage.light_essence[Storage.ESSENCE_HIGH] -= monster.monster.awaken_mats_light_high
                    summoner.storage.light_essence[Storage.ESSENCE_MID] -= monster.monster.awaken_mats_light_mid
                    summoner.storage.light_essence[Storage.ESSENCE_LOW] -= monster.monster.awaken_mats_light_low

                    summoner.storage.save()

                # Perform the awakening by instance's monster source ID
                monster.monster = monster.monster.awakens_to
                monster.save()

                response_data = {
                    'code': 'success',
                    'removeElement': '#awakenMonsterButton',
                }

            else:
                storage = summoner.storage.get_storage()
                available_essences = OrderedDict()

                for element, essences in monster.monster.get_awakening_materials().items():
                    available_essences[element] = OrderedDict()
                    for size, cost in essences.items():
                        if cost > 0:
                            available_essences[element][size] = {
                                'qty': storage[element][size],
                                'sufficient': storage[element][size] >= cost,
                            }

                context = {
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


def fusion_progress(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    fusions = Fusion.objects.all()

    context = {
        'view': 'fusion',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'fusions': fusions,
    }

    return render(request, 'herders/profile/fusion/base.html', context)


@username_case_redirect
def fusion_progress_detail(request, profile_name, monster_slug):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    context = {
        'view': 'fusion',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        try:
            fusion = Fusion.objects.get(product__bestiary_slug=monster_slug)
        except Fusion.DoesNotExist:
            return HttpResponseBadRequest()
        else:
            level = 10 + fusion.stars * 5
            ingredients = []

            # Check if fusion has been completed already
            fusion_complete = MonsterInstance.objects.filter(
                Q(owner=summoner), Q(monster=fusion.product) | Q(monster=fusion.product.awakens_to)
            ).exists()

            # Scan summoner's collection for instances each ingredient
            fusion_ready = True

            for ingredient in fusion.ingredients.all().select_related('awakens_from', 'awakens_to'):
                owned_ingredients = MonsterInstance.objects.filter(
                    Q(owner=summoner),
                    Q(monster=ingredient) | Q(monster=ingredient.awakens_from),
                ).order_by('-stars', '-level', '-monster__is_awakened')

                owned_ingredient_pieces = MonsterPiece.objects.filter(
                    Q(owner=summoner),
                    Q(monster=ingredient) | Q(monster=ingredient.awakens_from),
                ).first()

                # Determine if each individual requirement is met using highest evolved/leveled monster that is not ignored for fusion
                for owned_ingredient in owned_ingredients:
                    if not owned_ingredient.ignore_for_fusion:
                        acquired = True
                        evolved = owned_ingredient.stars >= fusion.stars
                        leveled = owned_ingredient.level >= level
                        awakened = owned_ingredient.monster.is_awakened
                        complete = acquired & evolved & leveled & awakened
                        break
                else:
                    if owned_ingredient_pieces:
                        acquired = owned_ingredient_pieces.can_summon()
                    else:
                        acquired = False

                    evolved = False
                    leveled = False
                    awakened = False
                    complete = False

                if not complete:
                    fusion_ready = False

                # Check if this ingredient is fusable
                sub_fusion = None
                sub_fusion_awakening_cost = None
                try:
                    sub_fusion = Fusion.objects.get(product=ingredient.awakens_from)
                except Fusion.DoesNotExist:
                    pass
                else:
                    if not acquired:
                        awakened_sub_fusion_ingredients = MonsterInstance.objects.filter(
                            monster__pk__in=sub_fusion.ingredients.values_list('pk', flat=True),
                            ignore_for_fusion=False,
                            owner=summoner,
                        )
                        sub_fusion_awakening_cost = sub_fusion.total_awakening_cost(awakened_sub_fusion_ingredients)

                ingredient_progress = {
                    'instance': ingredient,
                    'owned': owned_ingredients,
                    'pieces': owned_ingredient_pieces,
                    'complete': complete,
                    'acquired': acquired,
                    'evolved': evolved,
                    'leveled': leveled,
                    'awakened': awakened,
                    'is_fuseable': True if sub_fusion else False,
                    'sub_fusion_cost': sub_fusion_awakening_cost,
                }
                ingredients.append(ingredient_progress)

            awakened_owned_ingredients = MonsterInstance.objects.filter(
                monster__pk__in=fusion.ingredients.values_list('pk', flat=True),
                ignore_for_fusion=False,
                owner=summoner,
            )
            total_cost = fusion.total_awakening_cost(awakened_owned_ingredients)

            # Calculate fulfilled/missing essences
            essence_storage = summoner.storage.get_storage()

            total_missing = {
                element: {
                    size: total_cost[element][size] - essence_storage[element][size] if total_cost[element][size] > essence_storage[element][size] else 0
                    for size, qty in element_sizes.items()
                }
                for element, element_sizes in total_cost.items()
            }

            # Check if there are any missing
            essences_satisfied = True
            for sizes in total_missing.values():
                for qty in sizes.values():
                    if qty > 0:
                        essences_satisfied = False

            # Determine the total/missing essences including sub-fusions
            if fusion.sub_fusion_available():
                total_sub_fusion_cost = deepcopy(total_cost)
                for ingredient in ingredients:
                    if ingredient['sub_fusion_cost']:
                        for element, sizes in total_sub_fusion_cost.items():
                            for size, qty in sizes.items():
                                total_sub_fusion_cost[element][size] += ingredient['sub_fusion_cost'][element][size]

                # Now determine what's missing based on owner's storage
                storage = summoner.storage.get_storage()

                sub_fusion_total_missing = {
                    element: {
                            size: total_sub_fusion_cost[element][size] - storage[element][size] if total_sub_fusion_cost[element][size] > storage[element][size] else 0
                            for size, qty in element_sizes.items()
                        }
                    for element, element_sizes in total_sub_fusion_cost.items()
                    }

                sub_fusion_mats_satisfied = True
                for sizes in total_sub_fusion_cost.values():
                    for qty in sizes.values():
                        if qty > 0:
                            sub_fusion_mats_satisfied = False
            else:
                sub_fusion_total_missing = None
                sub_fusion_mats_satisfied = None

            progress = {
                'instance': fusion.product,
                'acquired': fusion_complete,
                'stars': fusion.stars,
                'level': level,
                'cost': fusion.cost,
                'ingredients': ingredients,
                'awakening_mats_cost': total_cost,
                'awakening_mats_sufficient': essences_satisfied,
                'awakening_mats_missing': total_missing,
                'sub_fusion_mats_missing': sub_fusion_total_missing,
                'sub_fusion_mats_sufficient': sub_fusion_mats_satisfied,
                'ready': fusion_ready,
            }

            context['fusion'] = progress

            return render(request, 'herders/profile/fusion/fusion_detail.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
def teams(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    add_team_group_form = AddTeamGroupForm()

    context = {
        'view': 'teams',
        'profile_name': profile_name,
        'summoner': summoner,
        'return_path': return_path,
        'is_owner': is_owner,
        'add_team_group_form': add_team_group_form,
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/teams/teams_base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


def team_list(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    # Get team objects for the summoner
    team_groups = TeamGroup.objects.filter(owner=summoner)

    context = {
        'profile_name': profile_name,
        'is_owner': is_owner,
        'team_groups': team_groups,
    }

    return render(request, 'herders/profile/teams/team_list.html', context)


@username_case_redirect
@login_required
def team_group_add(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    form = AddTeamGroupForm(request.POST or None)

    if is_owner:
        if form.is_valid() and request.method == 'POST':
            # Create the monster instance
            new_group = form.save(commit=False)
            new_group.owner = request.user.summoner
            new_group.save()

        return redirect(return_path)
    else:
        return PermissionDenied("Attempting to add group to profile you don't own.")


@username_case_redirect
@login_required
def team_group_edit(request, profile_name, group_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    team_group = get_object_or_404(TeamGroup, pk=group_id)

    form = EditTeamGroupForm(request.POST or None, instance=team_group)

    if is_owner:
        if form.is_valid() and request.method == 'POST':
            form.save()
            return redirect(return_path)
    else:
        return PermissionDenied("Editing a group you don't own")

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'form': form,
        'group_id': group_id,
        'return_path': return_path,
        'is_owner': is_owner,
        'view': 'teams',
    }
    return render(request, 'herders/profile/teams/team_group_edit.html', context)


@username_case_redirect
@login_required
def team_group_delete(request, profile_name, group_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    team_group = get_object_or_404(TeamGroup, pk=group_id)

    form = DeleteTeamGroupForm(request.POST or None)
    form.helper.form_action = request.path
    form.fields['reassign_group'].queryset = TeamGroup.objects.filter(owner=summoner).exclude(pk=group_id)

    context = {
        'view': 'teams',
        'profile_name': profile_name,
        'return_path': return_path,
        'is_owner': is_owner,
        'form': form,
    }

    if is_owner:
        if request.method == 'POST' and form.is_valid():
            list_of_teams = Team.objects.filter(group__pk=group_id)

            if request.POST.get('delete', False):
                list_of_teams.delete()
            else:
                new_group = form.cleaned_data['reassign_group']
                if new_group:
                    for team in list_of_teams:
                        team.group = new_group
                        team.save()
                else:
                    context['validation_errors'] = 'Please specify a group to reassign to.'

        if team_group.team_set.count() > 0:
            return render(request, 'herders/profile/teams/team_group_delete.html', context)
        else:
            messages.warning(request, 'Deleted team group %s' % team_group.name)
            team_group.delete()
            return redirect(return_path)
    else:
        return PermissionDenied()


@username_case_redirect
def team_detail(request, profile_name, team_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    team = get_object_or_404(Team, pk=team_id)

    team_effects = []
    if team.leader and team.leader.monster.all_skill_effects():
        for effect in team.leader.monster.all_skill_effects():
            if effect not in team_effects:
                team_effects.append(effect)

    for team_member in team.roster.all():
        if team_member.monster.all_skill_effects():
            for effect in team_member.monster.all_skill_effects():
                if effect not in team_effects:
                    team_effects.append(effect)

    context = {
        'view': 'teams',
        'profile_name': profile_name,
        'return_path': return_path,
        'is_owner': is_owner,
        'team': team,
        'team_buffs': team_effects,
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/teams/team_detail.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
@login_required
def team_edit(request, profile_name, team_id=None):
    return_path = reverse('herders:teams', kwargs={'profile_name': profile_name})
    if team_id:
        team = Team.objects.get(pk=team_id)
        edit_form = EditTeamForm(request.POST or None, instance=team)
    else:
        edit_form = EditTeamForm(request.POST or None)

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    # Limit form choices to objects owned by the current user.
    edit_form.fields['group'].queryset = TeamGroup.objects.filter(owner=summoner)
    edit_form.fields['leader'].queryset = MonsterInstance.objects.filter(owner=summoner)
    edit_form.fields['roster'].queryset = MonsterInstance.objects.filter(owner=summoner)
    edit_form.helper.form_action = request.path + '?next=' + return_path

    context = {
        'profile_name': profile_name,
        'return_path': return_path,
        'is_owner': is_owner,
        'view': 'teams',
    }

    if is_owner:
        edit_form.full_clean()  # re-clean due to updated querysets after form initialization

        if request.method == 'POST' and edit_form.is_valid():
            team = edit_form.save(commit=False)
            team.owner = summoner
            team.save()
            edit_form.save_m2m()

            messages.success(request, 'Saved changes to %s - %s.' % (team.group, team))

            return team_detail(request, profile_name, team.pk.hex)
    else:
        raise PermissionDenied()

    context['edit_team_form'] = edit_form
    return render(request, 'herders/profile/teams/team_edit.html', context)


@username_case_redirect
@login_required
def team_delete(request, profile_name, team_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    team = get_object_or_404(Team, pk=team_id)

    # Check for proper owner before deleting
    if request.user.summoner == team.group.owner:
        team.delete()
        messages.warning(request, 'Deleted team %s - %s.' % (team.group, team))
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@username_case_redirect
def runes(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    filter_form = FilterRuneForm(auto_id="filter_id_%s")
    filter_form.helper.form_action = reverse('herders:rune_inventory', kwargs={'profile_name': profile_name})

    context = {
        'view': 'runes',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'old_rune_count': RuneInstance.objects.filter(owner=summoner, substats__isnull=True).count(),
        'rune_filter_form': filter_form,
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/runes/base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
def rune_inventory(request, profile_name, view_mode=None, box_grouping=None):
    # If we passed in view mode or sort method, set the session variable and redirect back to base profile URL
    if view_mode:
        request.session['rune_inventory_view_mode'] = view_mode.lower()

    if box_grouping:
        request.session['rune_inventory_box_method'] = box_grouping.lower()

    if request.session.modified:
        return HttpResponse("Rune view mode cookie set")
    view_mode = request.session.get('rune_inventory_view_mode', 'box').lower()
    box_grouping = request.session.get('rune_inventory_box_method', 'slot').lower()

    if view_mode == 'crafts':
        return rune_inventory_crafts(request, profile_name)

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    rune_queryset = RuneInstance.objects.filter(owner=summoner).select_related('assigned_to', 'assigned_to__monster')
    total_count = rune_queryset.count()
    form = FilterRuneForm(request.POST or None)

    if form.is_valid():
        rune_filter = RuneInstanceFilter(form.cleaned_data, queryset=rune_queryset)
    else:
        rune_filter = RuneInstanceFilter(None, queryset=rune_queryset)

    filtered_count = rune_filter.qs.count()

    context = {
        'runes': rune_filter.qs,
        'total_count': total_count,
        'filtered_count': filtered_count,
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        if view_mode == 'box':
            rune_box = []
            if box_grouping == 'slot':
                rune_box.append({
                    'name': 'Slot 1',
                    'runes': rune_filter.qs.filter(slot=1)
                })
                rune_box.append({
                    'name': 'Slot 2',
                    'runes': rune_filter.qs.filter(slot=2)
                })
                rune_box.append({
                    'name': 'Slot 3',
                    'runes': rune_filter.qs.filter(slot=3)
                })
                rune_box.append({
                    'name': 'Slot 4',
                    'runes': rune_filter.qs.filter(slot=4)
                })
                rune_box.append({
                    'name': 'Slot 5',
                    'runes': rune_filter.qs.filter(slot=5)
                })
                rune_box.append({
                    'name': 'Slot 6',
                    'runes': rune_filter.qs.filter(slot=6)
                })
            elif box_grouping == 'grade':
                rune_box.append({
                    'name': '6*',
                    'runes': rune_filter.qs.filter(stars=6)
                })
                rune_box.append({
                    'name': '5*',
                    'runes': rune_filter.qs.filter(stars=5)
                })
                rune_box.append({
                    'name': '4*',
                    'runes': rune_filter.qs.filter(stars=4)
                })
                rune_box.append({
                    'name': '3*',
                    'runes': rune_filter.qs.filter(stars=3)
                })
                rune_box.append({
                    'name': '2*',
                    'runes': rune_filter.qs.filter(stars=2)
                })
                rune_box.append({
                    'name': '1*',
                    'runes': rune_filter.qs.filter(stars=1)
                })
            elif box_grouping == 'equipped':
                rune_box.append({
                    'name': 'Not Equipped',
                    'runes': rune_filter.qs.filter(assigned_to__isnull=True)
                })

                # Create a dictionary of monster PKs and their equipped runes
                monsters = OrderedDict()
                for rune in rune_filter.qs.filter(assigned_to__isnull=False).select_related('assigned_to', 'assigned_to__monster').order_by('assigned_to__monster__name', 'slot'):
                    if rune.assigned_to.pk not in monsters:
                        monsters[rune.assigned_to.pk] = {
                            'name': str(rune.assigned_to),
                            'runes': []
                        }

                    monsters[rune.assigned_to.pk]['runes'].append(rune)
                for monster_runes in monsters.values():
                    rune_box.append(monster_runes)
            elif box_grouping == 'type':
                for (type, type_name) in RuneInstance.TYPE_CHOICES:
                    rune_box.append({
                        'name': type_name,
                        'runes': rune_filter.qs.filter(type=type)
                    })

            context['runes'] = rune_box
            context['box_grouping'] = box_grouping
            template = 'herders/profile/runes/inventory.html'
        elif view_mode == 'grid':
            template = 'herders/profile/runes/inventory_grid.html'
        else:
            template = 'herders/profile/runes/inventory_table.html'

        return render(request, template, context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
def rune_inventory_crafts(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    context = {
        'profile_name': profile_name,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        craft_box = OrderedDict()
        for (craft, craft_name) in RuneCraftInstance.CRAFT_CHOICES:
            craft_box[craft_name] = OrderedDict()
            for rune, rune_name in RuneInstance.TYPE_CHOICES:
                craft_box[craft_name][rune_name] = RuneCraftInstance.objects.filter(owner=summoner, type=craft, rune=rune).order_by('stat', 'quality')

            # Immemorial
            craft_box[craft_name]['Immemorial'] = RuneCraftInstance.objects.filter(owner=summoner, type=craft, rune__isnull=True).order_by('stat', 'quality')

        context['crafts'] = craft_box

        return render(request, 'herders/profile/runes/inventory_crafts.html', context)
    else:
        return render(request, 'herders/profile/not_public.html')


@username_case_redirect
@login_required
def rune_add(request, profile_name):
    form = AddRuneInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:rune_add', kwargs={'profile_name': profile_name})
    template = loader.get_template('herders/profile/runes/add_form.html')

    if request.method == 'POST':
        if form.is_valid():
            # Create the rune instance
            new_rune = form.save(commit=False)
            new_rune.owner = request.user.summoner
            new_rune.save()

            messages.success(request, 'Added ' + str(new_rune))

            # Send back blank form
            form = AddRuneInstanceForm()
            form.helper.form_action = reverse('herders:rune_add', kwargs={'profile_name': profile_name})

            context = {'add_rune_form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'success',
                'html': template.render(context)
            }
        else:
            context = {'add_rune_form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'error',
                'html': template.render(context)
            }
    else:
        # Check for any pre-filled GET parameters
        slot = request.GET.get('slot', None)
        assigned_to = request.GET.get('assigned_to', None)

        try:
            assigned_monster = MonsterInstance.objects.get(owner=request.user.summoner, pk=assigned_to)
        except MonsterInstance.DoesNotExist:
            assigned_monster = None

        form = AddRuneInstanceForm(initial={
            'assigned_to': assigned_monster,
            'slot': slot if slot is not None else 1,
        })
        form.helper.form_action = reverse('herders:rune_add', kwargs={'profile_name': profile_name})

        # Return form filled in and errors shown
        context = {'add_rune_form': form}
        context.update(csrf(request))

        response_data = {
            'html': template.render(context)
        }

    return JsonResponse(response_data)


@username_case_redirect
@login_required
def rune_edit(request, profile_name, rune_id):
    rune = get_object_or_404(RuneInstance, pk=rune_id)
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    form = AddRuneInstanceForm(request.POST or None, instance=rune, auto_id='edit_id_%s')
    form.helper.form_action = reverse('herders:rune_edit', kwargs={'profile_name': profile_name, 'rune_id': rune_id})
    template = loader.get_template('herders/profile/runes/add_form.html')

    if is_owner:
        context = {'add_rune_form': form}
        context.update(csrf(request))

        if request.method == 'POST' and form.is_valid():
            rune = form.save()
            messages.success(request, 'Saved changes to ' + str(rune))
            form = AddRuneInstanceForm(auto_id='edit_id_%s')
            form.helper.form_action = reverse('herders:rune_edit', kwargs={'profile_name': profile_name, 'rune_id': rune_id})

            context = {'add_rune_form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'success',
                'html': template.render(context)
            }
        else:
            context = {'add_rune_form': form}
            context.update(csrf(request))

            # Return form filled in and errors shown
            response_data = {
                'code': 'error',
                'html': template.render(context)
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def rune_assign(request, profile_name, instance_id, slot=None):
    rune_queryset = RuneInstance.objects.filter(owner=request.user.summoner, assigned_to=None)
    filter_form = AssignRuneForm(request.POST or None, initial={'slot': slot}, prefix='assign')
    filter_form.helper.form_action = reverse('herders:rune_assign', kwargs={'profile_name': profile_name, 'instance_id': instance_id})

    if slot:
        rune_queryset = rune_queryset.filter(slot=slot)

    if request.method == 'POST' and filter_form.is_valid():
        rune_filter = RuneInstanceFilter(filter_form.cleaned_data, queryset=rune_queryset)
        template = loader.get_template('herders/profile/runes/assign_results.html')

        context = {
            'filter': rune_filter.qs,
            'profile_name': profile_name,
            'instance_id': instance_id,
        }
        context.update(csrf(request))

        response_data = {
            'code': 'results',
            'html': template.render(context)
        }
    else:
        rune_filter = RuneInstanceFilter(queryset=rune_queryset)
        template = loader.get_template('herders/profile/runes/assign_form.html')

        context = {
            'filter': rune_filter.qs,
            'form': filter_form,
            'profile_name': profile_name,
            'instance_id': instance_id,
        }
        context.update(csrf(request))

        response_data = {
            'code': 'success',
            'html': template.render(context)
        }

    return JsonResponse(response_data)


@username_case_redirect
@login_required
def rune_assign_choice(request, profile_name, instance_id, rune_id):
    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    rune = get_object_or_404(RuneInstance, pk=rune_id)

    if rune.assigned_to is not None:
        # TODO: Warn about removing from other monster?
        pass

    # Check for existing rune.
    existing_runes = monster.runeinstance_set.filter(slot=rune.slot)
    for existing_rune in existing_runes:
        existing_rune.assigned_to = None

    rune.assigned_to = monster
    rune.save()
    monster.save()

    response_data = {
        'code': 'success',
    }

    return JsonResponse(response_data)


@username_case_redirect
@login_required
def rune_unassign(request, profile_name, rune_id):
    rune = get_object_or_404(RuneInstance, pk=rune_id)
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        mon = rune.assigned_to
        rune.assigned_to = None
        rune.save()

        if mon:
            mon.save()

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required()
def rune_unassign_all(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    assigned_mons = []
    assigned_runes = RuneInstance.objects.filter(owner=summoner, assigned_to__isnull=False)
    number_assigned = assigned_runes.count()

    if is_owner:
        for rune in assigned_runes:
            if rune.assigned_to not in assigned_mons:
                assigned_mons.append(rune.assigned_to)

            rune.assigned_to = None
            rune.save()

        # Resave monster instances that had runes removed to recalc stats
        for mon in assigned_mons:
            mon.save()

        messages.success(request, 'Unassigned ' + str(number_assigned) + ' rune(s).')

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def rune_delete(request, profile_name, rune_id):
    rune = get_object_or_404(RuneInstance, pk=rune_id)
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        mon = rune.assigned_to
        messages.warning(request, 'Deleted ' + str(rune))
        rune.delete()
        if mon:
            mon.save()

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def rune_delete_all(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        # Delete the runes
        death_row = RuneInstance.objects.filter(owner=summoner)
        number_killed = death_row.count()
        assigned_mons = []
        for rune in death_row:
            if rune.assigned_to and rune.assigned_to not in assigned_mons:
                assigned_mons.append(rune.assigned_to)

        death_row.delete()

        # Delete the crafts
        RuneCraftInstance.objects.filter(owner=summoner).delete()
        messages.warning(request, 'Deleted ' + str(number_killed) + ' runes.')

        for mon in assigned_mons:
            mon.save()

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def rune_resave_all(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        for r in RuneInstance.objects.filter(owner=summoner, substats__isnull=True):
            r.save()

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def rune_craft_add(request, profile_name):
    form = AddRuneCraftInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:rune_craft_add', kwargs={'profile_name': profile_name})
    template = loader.get_template('herders/profile/runes/add_craft_form.html')

    if request.method == 'POST':
        if form.is_valid():
            # Create the monster instance
            new_craft = form.save(commit=False)
            new_craft.owner = request.user.summoner
            new_craft.save()

            rune_name = new_craft.get_rune_display() or ''
            messages.success(request, f'Added {rune_name} {new_craft.get_type_display()} {new_craft}')

            # Send back blank form
            form = AddRuneCraftInstanceForm()
            form.helper.form_action = reverse('herders:rune_craft_add', kwargs={'profile_name': profile_name})

            context = {'form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'success',
                'html': template.render(context)
            }
        else:
            context = {'form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'error',
                'html': template.render(context)
            }
    else:
        # Return form filled in and errors shown
        context = {'form': form}
        context.update(csrf(request))

        response_data = {
            'html': template.render(context)
        }

    return JsonResponse(response_data)


@username_case_redirect
@login_required
def rune_craft_edit(request, profile_name, craft_id):
    craft = get_object_or_404(RuneCraftInstance, pk=craft_id)
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    form = AddRuneCraftInstanceForm(request.POST or None, instance=craft)
    form.helper.form_action = reverse('herders:rune_craft_edit', kwargs={'profile_name': profile_name, 'craft_id': craft_id})
    template = loader.get_template('herders/profile/runes/add_craft_form.html')

    if is_owner:
        if request.method == 'POST' and form.is_valid():
            rune = form.save()
            messages.success(request, 'Saved changes to ' + str(rune))
            form = AddRuneInstanceForm()
            form.helper.form_action = reverse('herders:rune_craft_edit', kwargs={'profile_name': profile_name, 'craft_id': craft_id})

            context = {'form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'success',
                'html': template.render(context)
            }
        else:
            # Return form filled in and errors shown
            context = {'form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'error',
                'html': template.render(context)
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def rune_craft_delete(request, profile_name, craft_id):
    craft = get_object_or_404(RuneCraftInstance, pk=craft_id)
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        rune_name = craft.get_rune_display() or ''
        messages.warning(request, f'Deleted {rune_name} {craft.get_type_display()} {craft}')
        craft.delete()

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def import_export_home(request, profile_name):
    return render(request, 'herders/profile/import_export/base.html', context={
        'profile_name': profile_name,
        'view': 'importexport'
    })


@login_required
@csrf_exempt
def import_pcap(request, profile_name):
    request.upload_handlers = [TemporaryFileUploadHandler()]
    return _import_pcap(request, profile_name)


def _get_import_options(form_data):
    return {
        'clear_profile': form_data.get('clear_profile'),
        'default_priority': form_data.get('default_priority'),
        'lock_monsters': form_data.get('lock_monsters'),
        'minimum_stars': int(form_data.get('minimum_stars', 1)),
        'ignore_silver': form_data.get('ignore_silver'),
        'ignore_material': form_data.get('ignore_material'),
        'except_with_runes': form_data.get('except_with_runes'),
        'except_light_and_dark': form_data.get('except_light_and_dark'),
        'except_fusion_ingredient': form_data.get('except_fusion_ingredient'),
        'delete_missing_monsters': form_data.get('missing_monster_action'),
        'delete_missing_runes': form_data.get('missing_rune_action'),
        'ignore_validation_errors': form_data.get('ignore_validation'),
    }


@csrf_protect
def _import_pcap(request, profile_name):
    errors = []
    validation_failures = []

    if request.POST:
        form = ImportPCAPForm(request.POST, request.FILES)
        form.helper.form_action = reverse('herders:import_pcap', kwargs={'profile_name': profile_name})

        if form.is_valid():
            summoner = get_object_or_404(Summoner, user__username=request.user.username)
            uploaded_file = form.cleaned_data['pcap']
            import_options = _get_import_options(form.cleaned_data)

            if form.cleaned_data.get('save_defaults'):
                summoner.preferences['import_options'] = import_options
                summoner.save()

            try:
                data = parse_pcap(uploaded_file)
            except Exception as e:
                errors.append('Exception ' + str(type(e)) + ': ' + str(e))
            else:
                if data:
                    schema_errors, validation_errors = validate_sw_json(data, request.user.summoner)

                    if schema_errors:
                        errors += schema_errors

                    if validation_errors:
                        validation_failures += validation_errors

                    if not errors and (not validation_failures or import_options['ignore_validation_errors']):
                        # Queue the import
                        task = com2us_data_import.delay(data, summoner.pk, import_options)
                        request.session['import_task_id'] = task.task_id

                        return render(request, 'herders/profile/import_export/import_progress.html', context={'profile_name': profile_name})

                else:
                    errors.append("Unable to find Summoner's War data in the uploaded file")
    else:
        form = ImportPCAPForm(
            initial=request.user.summoner.preferences.get('import_options', {
                'ignore_silver': True
            })
        )

    context = {
        'profile_name': profile_name,
        'form': form,
        'errors': errors,
        'validation_failures': validation_failures,
        'view': 'importexport'
    }

    return render(request, 'herders/profile/import_export/import_pcap.html', context)


@username_case_redirect
@login_required
def import_sw_json(request, profile_name):
    errors = []
    validation_failures = []
    request.session['import_stage'] = None
    request.session['import_total'] = 0
    request.session['import_current'] = 0

    if request.POST:
        request.session['import_stage'] = None
        request.session.save()

        form = ImportSWParserJSONForm(request.POST, request.FILES)
        form.helper.form_action = reverse('herders:import_swparser', kwargs={'profile_name': profile_name})

        if form.is_valid():
            summoner = get_object_or_404(Summoner, user__username=request.user.username)
            uploaded_file = form.cleaned_data['json_file']
            import_options = _get_import_options(form.cleaned_data)

            if form.cleaned_data.get('save_defaults'):
                summoner.preferences['import_options'] = import_options
                summoner.save()

            try:
                data = json.load(uploaded_file)
            except ValueError as e:
                errors.append('Unable to parse file: ' + str(e))
            except AttributeError:
                errors.append('Issue opening uploaded file. Please try again.')
            else:
                schema_errors, validation_errors = validate_sw_json(data, request.user.summoner)

                if schema_errors:
                    errors.append(schema_errors)

                if validation_errors:
                    validation_failures += validation_errors

                if not errors and (not validation_failures or import_options['ignore_validation_errors']):
                    # Queue the import
                    task = com2us_data_import.delay(data, summoner.pk, import_options)
                    request.session['import_task_id'] = task.task_id

                    return render(request, 'herders/profile/import_export/import_progress.html', context={'profile_name': profile_name})
    else:
        form = ImportSWParserJSONForm(
            initial=request.user.summoner.preferences.get('import_options', {})
        )

    context = {
        'profile_name': profile_name,
        'form': form,
        'errors': errors,
        'validation_failures': validation_failures,
        'view': 'importexport',
    }

    return render(request, 'herders/profile/import_export/import_sw_json.html', context)


@username_case_redirect
@login_required
def import_status(request, profile_name):
    task_id = request.GET.get('id', request.session.get('import_task_id'))
    task = AsyncResult(task_id)

    if task:
        try:
            return JsonResponse({
                'status': task.status,
                'result': task.result,
            })
        except:
            return JsonResponse({
                'status': 'error',
            })
    else:
        raise Http404('Task ID not provided')


@username_case_redirect
@login_required
def export_win10_optimizer(request, profile_name):
    summoner = get_object_or_404(Summoner, user=request.user)

    export_data = export_win10(summoner)

    response = HttpResponse(export_data)
    response['Content-Disposition'] = 'attachment; filename=' + request.user.username + '_swarfarm_win10_optimizer_export.json'

    return response


# Data logs
DEFAULT_LOG_TIME_RANGE = {
    'timestamp__gte': '2018-09-13T00:00:00+00:00',
    'timestamp__lte': '2099-01-01T00:00:00+00:00'
}


@username_case_redirect
@login_required
def data_log_dashboard(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return HttpResponseForbidden()

    log_counts = {
        'magic_shop': summoner.shoprefreshlog_set.count(),
        'wish': summoner.wishlog_set.count(),
        'rune_crafting': summoner.craftrunelog_set.count(),
        'magic_box': summoner.magicboxcraft_set.count(),
        'summons': summoner.summonlog_set.count(),
        'dungeons': summoner.dungeonlog_set.count(),
        'rift_beast': summoner.riftdungeonlog_set.count(),
        'rift_raid': summoner.riftraidlog_set.count(),
        'world_boss': summoner.worldbosslog_set.count(),
    }

    total = reduce(lambda a, b: a + b, log_counts.values())

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'view': 'data_log',
        'counts': log_counts,
        'total': total,
    }

    return render(request, 'herders/profile/data_logs/dashboard.html', context)


@username_case_redirect
@login_required
def data_log_help(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return HttpResponseForbidden()

    return render(request, 'herders/profile/data_logs/help.html', {
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'view': 'data_log',
    })


def _log_data_table_view(request, profile_name, qs_attr, template):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return HttpResponseForbidden()

    form = FilterLogTimeRangeMixin(request.POST or None)

    if request.method == 'POST':
        # Process form with custom timestamps
        if form.is_valid():
            if form.cleaned_data['reset']:
                request.session['data_log_date_filter'] = {
                    **DEFAULT_LOG_TIME_RANGE
                }
            else:
                request.session['data_log_date_filter'] = {
                    'timestamp__gte': form.cleaned_data['start_time'].isoformat(),
                    'timestamp__lte': form.cleaned_data['end_time'].isoformat(),
                }
        else:
            messages.error(request, 'Unable to set specified time range.')

    time_filters = request.session.get('data_log_date_filter', DEFAULT_LOG_TIME_RANGE)

    qs = getattr(summoner, qs_attr).filter(**time_filters)
    paginator = Paginator(qs, 50)
    page = request.GET.get('page')

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'view': 'data_log',
        'logs': paginator.get_page(page),
        'form': form,
        'log_timestamp_start': time_filters['timestamp__gte'],
        'log_timestamp_end': time_filters['timestamp__lte'],
    }

    return render(request, template, context)


@username_case_redirect
@login_required
def data_log_magic_shop(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'shoprefreshlog_set',
        'herders/profile/data_logs/magic_shop.html',
    )


@username_case_redirect
@login_required
def data_log_wish(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'wishlog_set',
        'herders/profile/data_logs/wish.html',
    )


@username_case_redirect
@login_required
def data_log_rune_crafting(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'craftrunelog_set',
        'herders/profile/data_logs/rune_crafting.html',
    )


@username_case_redirect
@login_required
def data_log_magic_box(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'magicboxcraft_set',
        'herders/profile/data_logs/magic_box.html',
    )


@username_case_redirect
@login_required
def data_log_summons(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'summonlog_set',
        'herders/profile/data_logs/summons.html',
    )


@username_case_redirect
@login_required
def data_log_dungeons(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return HttpResponseForbidden()

    form = FilterDungeonLogForm(request.POST or None)
    qs = summoner.dungeonlog_set.all()

    if request.method == 'POST':
        if form.is_valid():
            # Apply filter form
            for key, value in form.cleaned_data.items():
                if value:
                    qs = qs.filter(**{key: value})

    paginator = Paginator(qs, 50)
    page = request.GET.get('page')

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'view': 'data_log',
        'logs': paginator.get_page(page),
        'form': form,
    }

    return render(request, 'herders/profile/data_logs/dungeons.html', context)


@username_case_redirect
@login_required
def data_log_rift_beast(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'riftdungeonlog_set',
        'herders/profile/data_logs/rift_beast.html',
    )


@username_case_redirect
@login_required
def data_log_rift_raid(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'riftraidlog_set',
        'herders/profile/data_logs/rift_raid.html',
    )


@username_case_redirect
@login_required
def data_log_world_boss(request, profile_name):
    return _log_data_table_view(
        request,
        profile_name,
        'worldbosslog_set',
        'herders/profile/data_logs/world_boss.html',
    )
