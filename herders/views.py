from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from .forms import RegisterUserForm, AddMonsterInstanceForm, EditMonsterInstanceForm, AwakenMonsterInstanceForm
from .models import Monster, Summoner, MonsterInstance


def index(request):
    context = {}
    return render(request, 'herders/index.html', context)


def register(request):
    context = {}
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)

        if form.is_valid():
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
                    return redirect('herders:profile')
        else:
            context['registration_failure'] = True
    else:
        form = RegisterUserForm()

    context['form'] = form
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
                return redirect('herders:profile')

        # If the above falls through then the login failed
        context['login_failure'] = True
        context['username'] = username

    # No data POSTed or the above login/auth failed.
    return render(request, 'herders/login.html', context)


def log_out(request):
    logout(request)
    return redirect('herders:index')


@login_required
def profile(request):
    context = {'add_monster_form': AddMonsterInstanceForm()}

    if request.user.is_authenticated():
        context['monster_stable'] = MonsterInstance.objects.filter(owner=request.user.summoner)

    return render(request, 'herders/profile/profile_view.html', context)


@login_required()
def add_monster_instance(request):
    if request.method == 'POST':
        form = AddMonsterInstanceForm(request.POST)

        if form.is_valid():
            # return render(request, 'herders/view_post_data.html', {'post_data': request.POST})
            # Create the monster instance
            new_monster = form.save(commit=False)
            new_monster.owner = request.user.summoner
            new_monster.save()

            return redirect('herders:profile')
    else:
        raise Http404("I don't know how this happened")


@login_required()
def edit_monster_instance(request, instance_id):
    context = {'add_monster_form': AddMonsterInstanceForm()}

    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    context['monster'] = monster

    if request.method == 'POST':
        form = EditMonsterInstanceForm(request.POST, instance=monster)

        if form.is_valid():
            form.save()
            return redirect('herders:profile')
        else:
            # Redisplay form with validation error messages
            form.helper.form_action = reverse('herders:edit_monster_instance', kwargs={'instance_id': monster.pk.hex})

            context['edit_monster_form'] = form
            context['validation_errors'] = form.non_field_errors()

            return render(request, 'herders/profile/profile_edit_monster.html', context)

    else:
        form = EditMonsterInstanceForm(instance=monster)
        form.helper.form_action = reverse('herders:edit_monster_instance', kwargs={'instance_id': monster.pk.hex})
        context['edit_monster_form'] = form

        return render(request, 'herders/profile/profile_edit_monster.html', context)


@login_required()
def delete_monster_instance(request, instance_id):
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    # Check for proper owner before deleting
    if request.user.summoner == monster.owner:
        monster.delete()
        return redirect('herders:profile')
    else:
        return HttpResponseForbidden()


@login_required()
def power_up_monster_instance(request, instance_id):
    return render(request, 'herders/unimplemented.html')


@login_required()
def awaken_monster_instance(request, instance_id):
    context = {'add_monster_form': AddMonsterInstanceForm()}

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

            return redirect('herders:profile')

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


@login_required
def fusion(request):
    return render(request, 'herders/unimplemented.html')


@login_required
def teams(request):
    return render(request, 'herders/unimplemented.html')
