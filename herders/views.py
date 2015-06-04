from collections import OrderedDict

from django.http import Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import RegisterUserForm, AddMonsterInstanceForm, EditMonsterInstanceForm, AwakenMonsterInstanceForm, \
    EditEssenceStorageForm, EditProfileForm
from .models import Monster, Summoner, MonsterInstance


def index(request):
    context = {
        'view_mode': 'list'
    }

    return render(request, 'herders/index.html', context)


def register(request):
    form = RegisterUserForm(request.POST or None
                            )
    if request.method == 'POST':
        if form.is_valid():
            try:
                # Create the user
                new_user = User.objects.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                )
                new_user.save()

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
                        return redirect('herders:profile', profile_name=user.username)
            except IntegrityError:
                form.add_error('username', 'Username already taken')

    context = {'form': form}
    return render(request, 'herders/register.html', context)


def log_in(request):
    context = {}

    if request.method == 'POST':
        username = request.POST['username']
        userpass = request.POST['userpass']

        user = authenticate(username=username, password=userpass)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('herders:profile', profile_name=user.username)

        # If the above falls through then the login failed
        context['login_failure'] = True
        context['username'] = username

    # No data POSTed or the above login/auth failed.
    return render(request, 'herders/login.html', context)


def log_out(request):
    logout(request)
    return redirect('herders:index')


def profile(request, profile_name=None, view_mode='list'):
    if profile_name is None:
        if request.user.is_authenticated():
            profile_name = request.user.username
        else:
            raise Http404('No user profilespecified and not logged in. ')

    summoner = get_object_or_404(Summoner, user__username=profile_name)

    # Determine if the person logged in is the one requesting the view
    is_owner = request.user.is_authenticated() and summoner.user == request.user

    context = {
        'add_monster_form': AddMonsterInstanceForm(),
        'profile_name': profile_name,
        'is_owner': is_owner,
        'view_mode': view_mode,
    }

    # Decide to show read only or full interface
    if is_owner or summoner.public:
        if view_mode.lower() == 'list':
            context['monster_stable'] = MonsterInstance.objects.filter(owner=summoner)
            return render(request, 'herders/profile/profile_view.html', context)
        elif view_mode.lower() == 'box':
            sort_method = 'grade'

            if sort_method == 'grade':
                monster_stable = OrderedDict()
                monster_stable['6*'] = MonsterInstance.objects.filter(owner=summoner, stars=6).order_by('-level', 'monster__name')
                monster_stable['5*'] = MonsterInstance.objects.filter(owner=summoner, stars=5).order_by('-level', 'monster__name')
                monster_stable['4*'] = MonsterInstance.objects.filter(owner=summoner, stars=4).order_by('-level', 'monster__name')
                monster_stable['3*'] = MonsterInstance.objects.filter(owner=summoner, stars=3).order_by('-level', 'monster__name')
                monster_stable['2*'] = MonsterInstance.objects.filter(owner=summoner, stars=2).order_by('-level', 'monster__name')
                monster_stable['1*'] = MonsterInstance.objects.filter(owner=summoner, stars=1).order_by('-level', 'monster__name')
            elif sort_method == 'level':
                monster_stable = OrderedDict()
                monster_stable['40-31'] = MonsterInstance.objects.filter(owner=summoner, level__gt=30).order_by('-level', '-stars', 'monster__name')
                monster_stable['30-21'] = MonsterInstance.objects.filter(owner=summoner, level__gt=20).filter(level__lte=30).order_by('-level', '-stars', 'monster__name')
                monster_stable['20-11'] = MonsterInstance.objects.filter(owner=summoner, level__gt=10).filter(level__lte=20).order_by('-level', '-stars', 'monster__name')
                monster_stable['10-1'] = MonsterInstance.objects.filter(owner=summoner, level__lte=10).order_by('-level', '-stars', 'monster__name')
            elif sort_method == 'attribute':
                monster_stable = OrderedDict()
                monster_stable['water'] = MonsterInstance.objects.filter(owner=summoner, monster__element=Monster.ELEMENT_WATER).order_by('-stars', '-level', 'monster__name')
                monster_stable['fire'] = MonsterInstance.objects.filter(owner=summoner, monster__element=Monster.ELEMENT_FIRE).order_by('-stars', '-level', 'monster__name')
                monster_stable['wind'] = MonsterInstance.objects.filter(owner=summoner, monster__element=Monster.ELEMENT_WIND).order_by('-stars', '-level', 'monster__name')
                monster_stable['light'] = MonsterInstance.objects.filter(owner=summoner, monster__element=Monster.ELEMENT_LIGHT).order_by('-stars', '-level', 'monster__name')
                monster_stable['dark'] = MonsterInstance.objects.filter(owner=summoner, monster__element=Monster.ELEMENT_DARK).order_by('-stars', '-level', 'monster__name')
            else:
                return Http404('Invalid sort method')

            context['monster_stable'] = monster_stable
            return render(request, 'herders/profile/profile_box.html', context)
    else:
        return render(request, 'herders/profile/not_public.html')


@login_required
def profile_edit(request):
    context = {
        'add_monster_form': AddMonsterInstanceForm(),
        'is_owner': True,  # Because of @login_required decorator
        'profile_name': request.user.username,
    }

    form = EditProfileForm(request.POST or None, instance=request.user.summoner)
    form.fields['rep_monster'].queryset = MonsterInstance.objects.filter(owner=request.user.summoner)

    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('herders:profile', profile_name=request.user.username)
    else:
        context['profile_form'] = form

    return render(request, 'herders/profile/profile_edit.html', context)


@login_required
def profile_storage(request):
    context = {
        'add_monster_form': AddMonsterInstanceForm(),
        'is_owner': True,
        'profile_name': request.user.username,
    }

    if request.method == 'POST':
        form = EditEssenceStorageForm(request.POST, instance=request.user.summoner)

        if form.is_valid():
            form.save()
            return redirect('herders:profile', profile_name=request.user.username)
        else:
            context['storage_form'] = form
    else:
        context['storage_form'] = EditEssenceStorageForm(instance=request.user.summoner)

    return render(request, 'herders/profile/profile_storage.html', context)


@login_required()
def monster_instance_add(request, profile_name):
    form = AddMonsterInstanceForm(request.POST or None)
    if form.is_valid() and request.method == 'POST':
        # Create the monster instance
        new_monster = form.save(commit=False)
        new_monster.owner = request.user.summoner
        new_monster.save()

        return redirect('herders:profile', profile_name=request.user.username)
    else:
        context = {
            'add_monster_form': form,
            'show_add_modal': True,
            'monster_stable': MonsterInstance.objects.filter(owner=request.user.summoner)
        }

        return render(request, 'herders/profile/profile_view.html', context)


def monster_instance_view(request, profile_name, instance_id):
    return render(request, 'herders/unimplemented.html')


def monster_instance_edit(request, profile_name, instance_id):
    context = {
        'add_monster_form': AddMonsterInstanceForm(),
        'profile_name': request.user.username,
    }

    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    context['monster'] = monster

    if request.method == 'POST':
        form = EditMonsterInstanceForm(request.POST, instance=monster)

        context['is_owner'] = True

        if form.is_valid():
            form.save()
            return redirect('herders:profile', profile_name=request.user.username)
        else:
            # Redisplay form with validation error messages
            form.helper.form_action = reverse('herders:view_monster_instance', kwargs={'instance_id': monster.pk.hex})

            context['edit_monster_form'] = form
            context['validation_errors'] = form.non_field_errors()

            return render(request, 'herders/profile/profile_monster_edit.html', context)

    else:
        # Check if current user owns the monster
        if monster.owner == request.user.summoner:

            form = EditMonsterInstanceForm(instance=monster)
            form.helper.form_action = reverse('herders:view_monster_instance', kwargs={'instance_id': monster.pk.hex})

            context['is_owner'] = True
            context['edit_monster_form'] = form

            return render(request, 'herders/profile/profile_monster_edit.html', context)
        else:
            return render(request, 'herders/profile/profile_monster_view.html', context)


@login_required()
def monster_instance_delete(request, profile_name, instance_id):
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    # Check for proper owner before deleting
    if request.user.summoner == monster.owner:
        monster.delete()
        return redirect('herders:profile', profile_name=request.user.username)
    else:
        return HttpResponseForbidden()


@login_required()
def monster_instance_power_up(request, profile_name, instance_id):
    return render(request, 'herders/unimplemented.html')


@login_required()
def monster_instance_awaken(request, profile_name, instance_id):
    context = {
        'add_monster_form': AddMonsterInstanceForm(),
        'profile_name': request.user.username,
        'is_owner': True,  # Because of @login_required decorator
    }

    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    context['monster'] = monster

    if request.method == 'POST':
        form = AwakenMonsterInstanceForm(request.POST)

        if form.is_valid() and monster.owner == request.user.summoner:
            # Subtract essences from inventory if requested
            if form.cleaned_data['subtract_materials']:
                summoner = Summoner.objects.get(user=request.user)

                if monster.monster.awaken_magic_mats_high:
                    summoner.storage_magic_high -= monster.monster.awaken_magic_mats_high
                if monster.monster.awaken_magic_mats_mid:
                    summoner.storage_magic_mid -= monster.monster.awaken_magic_mats_mid
                if monster.monster.awaken_magic_mats_low:
                    summoner.storage_magic_low -= monster.monster.awaken_magic_mats_low

                if monster.monster.element == Monster.ELEMENT_FIRE:
                    if monster.monster.awaken_ele_mats_high:
                        summoner.storage_fire_high -= monster.monster.awaken_ele_mats_high
                    if monster.monster.awaken_ele_mats_mid:
                        summoner.storage_fire_mid -= monster.monster.awaken_ele_mats_mid
                    if monster.monster.awaken_ele_mats_low:
                        summoner.storage_fire_low -= monster.monster.awaken_ele_mats_low
                elif monster.monster.element == Monster.ELEMENT_WATER:
                    if monster.monster.awaken_ele_mats_high:
                        summoner.storage_water_high -= monster.monster.awaken_ele_mats_high
                    if monster.monster.awaken_ele_mats_mid:
                        summoner.storage_water_mid -= monster.monster.awaken_ele_mats_mid
                    if monster.monster.awaken_ele_mats_low:
                        summoner.storage_water_low -= monster.monster.awaken_ele_mats_low
                elif monster.monster.element == Monster.ELEMENT_WIND:
                    if monster.monster.awaken_ele_mats_high:
                        summoner.storage_wind_high -= monster.monster.awaken_ele_mats_high
                    if monster.monster.awaken_ele_mats_mid:
                        summoner.storage_wind_mid -= monster.monster.awaken_ele_mats_mid
                    if monster.monster.awaken_ele_mats_low:
                        summoner.storage_wind_low -= monster.monster.awaken_ele_mats_low
                elif monster.monster.element == Monster.ELEMENT_DARK:
                    if monster.monster.awaken_ele_mats_high:
                        summoner.storage_dark_high -= monster.monster.awaken_ele_mats_high
                    if monster.monster.awaken_ele_mats_mid:
                        summoner.storage_dark_mid -= monster.monster.awaken_ele_mats_mid
                    if monster.monster.awaken_ele_mats_low:
                        summoner.storage_dark_low -= monster.monster.awaken_ele_mats_low
                elif monster.monster.element == Monster.ELEMENT_LIGHT:
                    if monster.monster.awaken_ele_mats_high:
                        summoner.storage_light_high -= monster.monster.awaken_ele_mats_high
                    if monster.monster.awaken_ele_mats_mid:
                        summoner.storage_light_mid -= monster.monster.awaken_ele_mats_mid
                    if monster.monster.awaken_ele_mats_low:
                        summoner.storage_light_low -= monster.monster.awaken_ele_mats_low

                summoner.save()

            # Perform the awakening by instance's monster source ID
            monster.monster = monster.monster.awakens_to()
            monster.save()

            return redirect('herders:profile', profile_name=request.user.username)

    else:
        # Set up form
        form = AwakenMonsterInstanceForm()
        form.helper.form_action = reverse('herders:awaken_monster_instance', kwargs={'instance_id': monster.pk.hex})
        context['awaken_monster_form'] = form

        # Retreive list of awakening materials from summoner profile
        summoner = Summoner.objects.get(user=request.user)

        available_materials = {
            'storage_magic_low': summoner.storage_magic_low,
            'storage_magic_mid': summoner.storage_magic_mid,
            'storage_magic_high': summoner.storage_magic_high
        }

        if monster.monster.element == Monster.ELEMENT_FIRE:
            available_materials['storage_ele_low'] = summoner.storage_fire_low
            available_materials['storage_ele_mid'] = summoner.storage_fire_mid
            available_materials['storage_ele_high'] = summoner.storage_fire_high
        elif monster.monster.element == Monster.ELEMENT_WATER:
            available_materials['storage_ele_low'] = summoner.storage_water_low
            available_materials['storage_ele_mid'] = summoner.storage_water_mid
            available_materials['storage_ele_high'] = summoner.storage_water_high
        elif monster.monster.element == Monster.ELEMENT_WIND:
            available_materials['storage_ele_low'] = summoner.storage_wind_low
            available_materials['storage_ele_mid'] = summoner.storage_wind_mid
            available_materials['storage_ele_high'] = summoner.storage_wind_high
        elif monster.monster.element == Monster.ELEMENT_DARK:
            available_materials['storage_ele_low'] = summoner.storage_dark_low
            available_materials['storage_ele_mid'] = summoner.storage_dark_mid
            available_materials['storage_ele_high'] = summoner.storage_dark_high
        elif monster.monster.element == Monster.ELEMENT_LIGHT:
            available_materials['storage_ele_low'] = summoner.storage_light_low
            available_materials['storage_ele_mid'] = summoner.storage_light_mid
            available_materials['storage_ele_high'] = summoner.storage_light_high

        context['available_materials'] = available_materials

        return render(request, 'herders/profile/profile_awaken.html', context)


@login_required
def fusion(request):
    return render(request, 'herders/unimplemented.html')


@login_required
def teams(request):
    return render(request, 'herders/unimplemented.html')


def bestiary(request, monster_element=None):
    context = dict()

    if monster_element is not None:
        if monster_element == 'all':
            context['monster_list'] = Monster.objects.all()
        else:
            context['monster_list'] = get_list_or_404(Monster, element=monster_element)
    else:
        context['no_filter'] = True

    return render(request, 'herders/bestiary.html', context)


def bestiary_detail(request, monster_id):
    return render(request, 'herders/unimplemented.html')
