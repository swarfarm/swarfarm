from collections import OrderedDict

from django.http import Http404, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.db import IntegrityError
from django.db.models import Q
from django.forms.formsets import formset_factory
from django.forms.models import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.templatetags.static import static

from .forms import *
from .models import Monster, Summoner, MonsterInstance, MonsterSkillEffect, Fusion, TeamGroup, Team
from .fusion import essences_missing, total_awakening_cost


def register(request):
    form = RegisterUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
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
            except IntegrityError:
                form.add_error('username', 'Username already taken')

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


@login_required
def profile_delete(request, profile_name):
    user = request.user
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    form = DeleteProfileForm(request.POST or None)
    form.helper.form_action = reverse('herders:profile_delete', kwargs={'profile_name': profile_name})

    context = {
        'form': form,
    }
    if is_owner:
        if request.method == 'POST' and form.is_valid():
            logout(request)
            user.delete()
            messages.success(request, 'Your profile has been deleted.')
            return redirect('news:latest_news')

        return render(request, 'herders/profile/profile_delete.html', context)
    else:
        return HttpResponseForbidden("You don't own this profile")


@login_required
def following(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_following', kwargs={'profile_name': profile_name})
    )

    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'summoner': summoner,
        'view': 'following',
        'return_path': return_path,
    }

    return render(request, 'herders/profile/following/list.html', context)


@login_required
def follow_add(request, profile_name, follow_username):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )

    summoner = get_object_or_404(Summoner, user__username=profile_name)
    new_follower = get_object_or_404(Summoner, user__username=follow_username)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if is_owner:
        summoner.following.add(new_follower)
        messages.success(request, 'Now following %s' % new_follower.user.username)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@login_required
def follow_remove(request, profile_name, follow_username):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )

    summoner = get_object_or_404(Summoner, user__username=profile_name)
    removed_follower = get_object_or_404(Summoner, user__username=follow_username)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if is_owner:
        summoner.following.remove(removed_follower)
        messages.success(request, 'Unfollowed %s' % removed_follower.user.username)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


def profile(request, profile_name=None, view_mode=None, sort_method=None):
    if profile_name is None:
        if request.user.is_authenticated():
            profile_name = request.user.username
        else:
            raise Http404('No user profile specified and not logged in.')

    summoner = get_object_or_404(Summoner, user__username=profile_name)

    # Determine if the person logged in is the one requesting the view
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    # If we passed in view mode or sort method, set the session variable and redirect back to base profile URL
    if view_mode:
        request.session['profile_view_mode'] = view_mode

    if sort_method:
        request.session['profile_sort_method'] = sort_method

    if request.session.modified:
        return redirect('herders:profile_default', profile_name=profile_name)

    view_mode = request.session.get('profile_view_mode', 'list')
    sort_method = request.session.get('profile_sort_method', 'grade')

    context = {
        'add_monster_form': AddMonsterInstanceForm(),
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'view_mode': view_mode,
        'sort_method': sort_method,
        'return_path': request.path,
        'view': 'profile',
    }

    if is_owner or summoner.public:
        if view_mode.lower() == 'list':
            context['monster_stable'] = MonsterInstance.objects.select_related('monster', 'monster__leader_skill').filter(owner=summoner)
            context['buff_list'] = MonsterSkillEffect.objects.filter(is_buff=True).exclude(icon_filename='').order_by('name')
            context['debuff_list'] = MonsterSkillEffect.objects.filter(is_buff=False).exclude(icon_filename='').order_by('name')
            context['other_effect_list'] = MonsterSkillEffect.objects.filter(icon_filename='').order_by('name')

            return render(request, 'herders/profile/profile_list_view.html', context)
        elif view_mode.lower() == 'box':
            if sort_method == 'grade':
                monster_stable = OrderedDict()
                monster_stable['6*'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, stars=6).order_by('-level', 'monster__name')
                monster_stable['5*'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, stars=5).order_by('-level', 'monster__name')
                monster_stable['4*'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, stars=4).order_by('-level', 'monster__name')
                monster_stable['3*'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, stars=3).order_by('-level', 'monster__name')
                monster_stable['2*'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, stars=2).order_by('-level', 'monster__name')
                monster_stable['1*'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, stars=1).order_by('-level', 'monster__name')
            elif sort_method == 'level':
                monster_stable = OrderedDict()
                monster_stable['40'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, level=40).order_by('-level', '-stars', 'monster__name')
                monster_stable['39-31'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, level__gt=30).filter(level__lt=40).order_by('-level', '-stars', 'monster__name')
                monster_stable['30-21'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, level__gt=20).filter(level__lte=30).order_by('-level', '-stars', 'monster__name')
                monster_stable['20-11'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, level__gt=10).filter(level__lte=20).order_by('-level', '-stars', 'monster__name')
                monster_stable['10-1'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, level__lte=10).order_by('-level', '-stars', 'monster__name')
            elif sort_method == 'attribute':
                monster_stable = OrderedDict()
                monster_stable['water'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, monster__element=Monster.ELEMENT_WATER).order_by('-stars', '-level', 'monster__name')
                monster_stable['fire'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, monster__element=Monster.ELEMENT_FIRE).order_by('-stars', '-level', 'monster__name')
                monster_stable['wind'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, monster__element=Monster.ELEMENT_WIND).order_by('-stars', '-level', 'monster__name')
                monster_stable['light'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, monster__element=Monster.ELEMENT_LIGHT).order_by('-stars', '-level', 'monster__name')
                monster_stable['dark'] = MonsterInstance.objects.select_related('monster').filter(owner=summoner, monster__element=Monster.ELEMENT_DARK).order_by('-stars', '-level', 'monster__name')
            else:
                raise Http404('Invalid sort method')

            context['monster_stable'] = monster_stable
            return render(request, 'herders/profile/profile_box.html', context)
        else:
            raise Http404('Unknown profile view mode')
    else:
        return render(request, 'herders/profile/not_public.html')


@login_required
def profile_edit(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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

            messages.success(request, 'Your profile has been updated.')
            return redirect(return_path)
        else:
            return render(request, 'herders/profile/profile_edit.html', context)
    else:
        return HttpResponseForbidden()


@login_required
def profile_storage(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    form = EditEssenceStorageForm(request.POST or None, instance=request.user.summoner)
    form.helper.form_action = request.path + '?next=' + return_path

    context = {
        'is_owner': is_owner,
        'profile_name': request.user.username,
        'summoner': summoner,
        'storage_form': form,
        'view': 'storage',
        'profile_view': 'materials',
    }

    if request.method == 'POST' and form.is_valid():
        form.save()

        if request.POST.get('save', None):
            return redirect(return_path)

    return render(request, 'herders/essence_storage.html', context)


@login_required()
def monster_instance_add(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    form = AddMonsterInstanceForm(request.POST or None)

    if form.is_valid() and request.method == 'POST':
        # Create the monster instance
        new_monster = form.save(commit=False)
        new_monster.owner = request.user.summoner
        new_monster.save()

        messages.success(request, 'Added %s to your collection.' % new_monster)
        return redirect(return_path)
    else:
        # Re-show same page but with form filled in and errors shown
        context = {
            'profile_name': profile_name,
            'summoner': summoner,
            'add_monster_form': form,
            'return_path': return_path,
            'is_owner': is_owner,
            'view': 'profile',
        }
        return render(request, 'herders/profile/profile_monster_add.html', context)


@login_required()
def monster_instance_quick_add(request, profile_name, monster_id, stars, level):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    monster_to_add = get_object_or_404(Monster, pk=monster_id)

    if is_owner:
        new_monster = MonsterInstance.objects.create(owner=summoner, monster=monster_to_add, stars=stars, level=level, fodder=True, notes='', priority=MonsterInstance.PRIORITY_DONE)
        messages.success(request, 'Added %s to your collection.' % new_monster)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@login_required()
def monster_instance_bulk_add(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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
        'bulk_add_formset': formset,
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
                            new_instance.save()
                            messages.success(request, 'Added %s to your collection.' % new_instance)
                    except ObjectDoesNotExist:
                        # Blank form, don't care
                        pass

                return redirect(return_path)
    else:
        raise PermissionDenied("Trying to bulk add to profile you don't own")

    return render(request, 'herders/profile/profile_monster_bulk_add.html', context)


def monster_instance_view(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        request.path
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    try:
        instance = MonsterInstance.objects.select_related('monster', 'monster__leader_skill').prefetch_related('monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        raise Http404()

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
        'profile_name': request.user.username,
        'summoner': summoner,
        'return_path': return_path,
        'instance': instance,
        'skills': skills,
        'is_owner': is_owner,
        'view': 'profile',
    }

    # Add in the forms if you're the owner.
    if is_owner:
        # Edit form requires a lot of customization based on skills
        edit_form = EditMonsterInstanceForm(request.POST or None, instance=instance)
        edit_form.helper.form_action = reverse('herders:monster_instance_edit', kwargs={'profile_name': profile_name, 'instance_id': instance.pk.hex}) + '?next=' + return_path
        if len(skills) >= 1 and skills[0]['skill'].max_level > 1:

            edit_form.helper['skill_1_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_1", data_skill_field=edit_form['skill_1_level'].auto_id),
            )
            edit_form.helper['skill_1_level'].wrap(Field, min=1, max=skills[0]['skill'].max_level)
            edit_form.fields['skill_1_level'].label = skills[0]['skill'].name + " Level"
        else:
            edit_form.helper['skill_1_level'].wrap(Div, css_class="hidden")

        if len(skills) >= 2 and skills[1]['skill'].max_level > 1:
            edit_form.helper['skill_2_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_2", data_skill_field=edit_form['skill_2_level'].auto_id),
                min=1,
                max=skills[1]['skill'].max_level,
            )
            edit_form.helper['skill_2_level'].wrap(Field, min=1, max=skills[1]['skill'].max_level)
            edit_form.fields['skill_2_level'].label = skills[1]['skill'].name + " Level"
        else:
            edit_form.helper['skill_2_level'].wrap(Div, css_class="hidden")

        if len(skills) >= 3 and skills[2]['skill'].max_level > 1:
            edit_form.helper['skill_3_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_3", data_skill_field=edit_form['skill_3_level'].auto_id),
                min=1,
                max=skills[2]['skill'].max_level,
            )
            edit_form.helper['skill_3_level'].wrap(Field, min=1, max=skills[2]['skill'].max_level)
            edit_form.fields['skill_3_level'].label = skills[2]['skill'].name + " Level"
        else:
            edit_form.helper['skill_3_level'].wrap(Div, css_class="hidden")

        if len(skills) >= 4 and skills[3]['skill'].max_level > 1:
            edit_form.helper['skill_4_level'].wrap(
                FieldWithButtons,
                StrictButton("Max", name="Set_Max_Skill_4", data_skill_field=edit_form['skill_4_level'].auto_id),
                min=1,
                max=skills[1]['skill'].max_level,
            )
            edit_form.helper['skill_4_level'].wrap(Field, min=1, max=skills[3]['skill'].max_level)
            edit_form.fields['skill_4_level'].label = skills[3]['skill'].name + " Level"
        else:
            edit_form.helper['skill_4_level'].wrap(Div, css_class="hidden")

        context['edit_form'] = edit_form

        awaken_form = AwakenMonsterInstanceForm()
        awaken_form.helper.form_action = reverse('herders:monster_instance_awaken', kwargs={'profile_name': profile_name, 'instance_id': instance.pk.hex}) + '?next=' + return_path
        context['awaken_form'] = awaken_form

        storage = summoner.get_storage()
        available_essences = OrderedDict()

        for element, essences in instance.monster.get_awakening_materials().iteritems():
            available_essences[element] = OrderedDict()
            for size, cost in essences.iteritems():
                available_essences[element][size] = dict()
                available_essences[element][size]['qty'] = storage[element][size]
                available_essences[element][size]['sufficient'] = storage[element][size] >= cost

        context['available_essences'] = available_essences

        PowerUpFormset = formset_factory(PowerUpMonsterInstanceForm, extra=5, max_num=5)
        context['power_up_form'] = PowerUpFormset()
        context['power_up_form_action'] = reverse('herders:monster_instance_power_up', kwargs={'profile_name': profile_name, 'instance_id': instance.pk.hex}) + '?next=' + return_path

    if is_owner or summoner.public:
        return render(request, 'herders/profile/profile_monster_view.html', context)
    else:
        return render(request, 'herders/profile/not_public.html')


@login_required()
def monster_instance_edit(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    instance = get_object_or_404(MonsterInstance, pk=instance_id)

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
    form.helper.form_action = request.path + '?next=' + return_path
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

    context = {
        'profile_name': request.user.username,
        'summoner': summoner,
        'return_path': return_path,
        'monster': instance,
        'is_owner': is_owner,
        'edit_monster_form': form,
        'view': 'profile',
    }

    if is_owner:
        if request.method == 'POST':
            if form.is_valid():
                monster = form.save(commit=False)
                monster.save()

                messages.success(request, 'Saved changes to %s.' % monster)
                return redirect(return_path)
    else:
        raise PermissionDenied()

    return render(request, 'herders/profile/profile_monster_edit.html', context)


@login_required()
def monster_instance_delete(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    # Check for proper owner before deleting
    if request.user.summoner == monster.owner:
        messages.success(request, 'Deleted ' + str(monster))
        monster.delete()

        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@login_required()
def monster_instance_power_up(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    PowerUpFormset = formset_factory(PowerUpMonsterInstanceForm, extra=5, max_num=5)

    if request.method == 'POST':
        formset = PowerUpFormset(request.POST)
    else:
        formset = PowerUpFormset()

    context = {
        'profile_name': request.user.username,
        'return_path': return_path,
        'monster': monster,
        'is_owner': is_owner,
        'power_up_formset_action': request.path + '?next=' + return_path,
        'power_up_formset': formset,
        'view': 'profile',
    }

    food_monsters = []
    validation_errors = {}

    if is_owner:
        if request.method == 'POST':
            # return render(request, 'herders/view_post_data.html', {'post_data': request.POST})
            if formset.is_valid():
                # Create list of submitted food monsters
                for instance in formset.cleaned_data:
                    # Some fields may be blank if user skipped a form input or didn't fill in all 5
                    if instance:
                        food_monsters.append(instance['monster'])

                # Check that all food monsters are unique - This is done whether or not user bypassed evolution checks
                if len(food_monsters) != len(set(food_monsters)):
                    validation_errors['food_monster_unique'] = "You submitted duplicate food monsters. Please select unique monsters for each slot."

                # Check that monster is not being fed to itself
                for food in food_monsters:
                    if food == monster:
                        validation_errors['base_food_same'] = "You can't feed a monster to itself. "

                is_evolution = request.POST.get('evolve', False)

                # Perform validation checks for evolve action
                if is_evolution:
                    # Check constraints on evolving (or not, if form element was set)
                    if not request.POST.get('ignore_errors', False):
                        # Check monster level and stars
                        if monster.stars >= 6:
                            validation_errors['base_monster_stars'] = "%s is already at 6 stars." % monster.monster.name

                        if monster.level != monster.max_level_from_stars():
                            validation_errors['base_monster_level'] = "%s is not at max level for the current star rating (Lvl %s)." % (monster.monster.name, monster.monster.max_level_from_stars())

                        # Check number of fodder monsters
                        if len(food_monsters) < monster.stars:
                            validation_errors['food_monster_quantity'] = "Evolution requres %s food monsters." % monster.stars

                        # Check fodder star ratings - must be same as monster
                        for food in food_monsters:
                            if food.stars != monster.stars:
                                if 'food_monster_stars' not in validation_errors:
                                    validation_errors['food_monster_stars'] = "All food monsters must be %s stars." % monster.stars
                    else:
                        # Record state of ignore evolve rules for form redisplay
                        context['ignore_evolve_checked'] = True

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
                            messages.success(request, 'Deleted %s' % food)
                            food.delete()
                        else:
                            raise PermissionDenied("Trying to delete a monster you don't own")

                    # Redirect back to return path if evolved, or go to edit screen if power up
                    if is_evolution:
                        return redirect(return_path)
                    else:
                        return redirect(
                            reverse('herders:monster_instance_view', kwargs={'profile_name':profile_name, 'instance_id': instance_id})
                        )
            else:
                context['form_errors'] = formset.errors

    else:
        raise PermissionDenied("Trying to power up or evolve a monster you don't own")

    # Any errors in the form will fall through to here and be displayed
    context['validation_errors'] = validation_errors
    return render(request, 'herders/profile/profile_power_up.html', context)


@login_required()
def monster_instance_awaken(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    if monster.monster.is_awakened:
        return redirect(return_path)

    form = AwakenMonsterInstanceForm(request.POST or None)
    form.helper.form_action = request.path + '?next=' + return_path

    context = {
        'profile_name': request.user.username,
        'summoner': summoner,
        'is_owner': is_owner,  # Because of @login_required decorator
        'return_path': return_path,
        'monster': monster,
        'awaken_monster_form': form,
    }

    if request.method == 'POST' and form.is_valid() and is_owner:
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
        monster.monster = monster.monster.awakens_to
        monster.save()

        messages.success(request, "Awakened " + str(monster.monster.awakens_from) + " to " + str(monster.monster))

        return redirect(return_path)

    else:
        storage = summoner.get_storage()
        available_essences = OrderedDict()

        for element, essences in monster.monster.get_awakening_materials().iteritems():
            available_essences[element] = OrderedDict()
            for size, cost in essences.iteritems():
                available_essences[element][size] = dict()
                available_essences[element][size]['qty'] = storage[element][size]
                available_essences[element][size]['sufficient'] = storage[element][size] >= cost

        context['available_essences'] = available_essences

        return render(request, 'herders/profile/profile_monster_awaken.html', context)


@login_required()
def monster_instance_duplicate(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    )
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    # Check for proper owner before copying
    if request.user.summoner == monster.owner:
        newmonster = monster
        newmonster.pk = None
        newmonster.save()
        messages.success(request, 'Succesfully copied ' + str(newmonster))

        return redirect(return_path)
    else:
        return HttpResponseForbidden()


def fusion_progress(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:fusion', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    context = {
        'view': 'fusion',
        'profile_name': profile_name,
        'summoner': summoner,
        'return_path': return_path,
        'is_owner': is_owner,
    }

    fusions = Fusion.objects.all().select_related()
    progress = OrderedDict()

    if is_owner or summoner.public:
        for fusion in fusions:
            level = 10 + fusion.stars * 5
            ingredients = []

            # Check if fusion has been completed already
            fusion_complete = MonsterInstance.objects.filter(
                Q(owner=summoner), Q(monster=fusion.product) | Q(monster=fusion.product.awakens_to)
            ).filter(ignore_for_fusion=False).count() > 0

            # Scan summoner's collection for instances each ingredient
            for ingredient in fusion.ingredients.all().select_related('awakens_from', 'awakens_to'):
                owned_ingredients = MonsterInstance.objects.filter(
                    Q(owner=summoner),
                    Q(monster=ingredient) | Q(monster=ingredient.awakens_from),
                ).order_by('-stars', '-level', '-monster__is_awakened')

                sub_fusion_available = Fusion.objects.filter(product=ingredient.awakens_from).exists()

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
                    acquired = False
                    evolved = False
                    leveled = False
                    awakened = False
                    complete = False

                ingredient_progress = {
                    'instance': ingredient,
                    'sub_fusion_available': sub_fusion_available,
                    'owned': owned_ingredients,
                    'complete': complete,
                    'acquired': acquired,
                    'evolved': evolved,
                    'leveled': leveled,
                    'awakened': awakened,
                }
                ingredients.append(ingredient_progress)

            fusion_ready = True
            for i in ingredients:
                if not i['complete']:
                    fusion_ready = False

            total_cost = total_awakening_cost(ingredients)
            total_missing = essences_missing(summoner.get_storage(), total_cost)

            progress[fusion.product.name] = {
                'instance': fusion.product,
                'acquired': fusion_complete,
                'stars': fusion.stars,
                'level': level,
                'cost': fusion.cost,
                'ingredients': ingredients,
                'awakening_materials': {
                    'total_cost': total_cost,
                    'missing': total_missing,
                },
                'ready': fusion_ready,
            }

        # Iterate through again and find any sub-fusions that are possible. Add their missing essences together for a total count
        from copy import deepcopy
        for monster, fusion in progress.iteritems():
            # print 'Checking sub-fusions for ' + monster
            combined_total_cost = deepcopy(fusion['awakening_materials']['total_cost'])
            sub_fusions_found = False

            # Check if ingredients for this fusion are fuseable themselves
            for ingredient in fusion['ingredients']:
                if ingredient['sub_fusion_available'] and not ingredient['acquired']:
                    sub_fusions_found = True
                    # print '    Found sub-fusion for ' + str(ingredient['instance'])
                    # Get the totals for the sub-fusions and add to the current fusion cost
                    sub_fusion = progress.get(ingredient['instance'].awakens_from.name, None)
                    for element, sizes in fusion['awakening_materials']['total_cost'].iteritems():
                        # print '        element: ' + str(element)
                        if element not in combined_total_cost:
                            combined_total_cost[element] = OrderedDict()

                        # print sub_fusion['awakening_materials']['missing']

                        for size in set(sizes.keys() + sub_fusion['awakening_materials']['missing'][element].keys()):
                            # print '        size: ' + size
                            # print '            sub fusion:               ' + str(sub_fusion['awakening_materials']['total_cost'][element].get(size, 0))
                            # print '            current combined_total_cost: ' + str(combined_total_cost[element].get(size, 0))
                            combined_total_cost[element][size] = combined_total_cost[element].get(size, 0) + sub_fusion['awakening_materials']['total_cost'][element].get(size, 0)
                            # print '            new     combined_total_cost: ' + str(combined_total_cost[element][size])

            if sub_fusions_found:
                fusion['awakening_materials']['combined'] = essences_missing(summoner.get_storage(), combined_total_cost)

        context['fusions'] = progress

        return render(request, 'herders/profile/profile_fusion.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


def fusion_perform(request, profile_name, fusion_product_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:fusion', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    context = {
        'view': 'fusion',
        'profile_name': profile_name,
        'summoner': summoner,
        'return_path': return_path,
        'is_owner': is_owner,
    }

    fusion = Fusion.objects.get(product__pk=fusion_product_id)


def teams(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    # Get team objects for the summoner
    team_groups = TeamGroup.objects.filter(owner=summoner)

    context = {
        'profile_name': profile_name,
        'is_owner': is_owner,
        'team_groups': team_groups,
    }

    return render(request, 'herders/profile/teams/team_list.html', context)


@login_required
def team_group_add(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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


@login_required
def team_group_edit(request, profile_name, group_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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


@login_required
def team_group_delete(request, profile_name, group_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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
            messages.success(request, 'Deleted team group %s' % team_group.name)
            team_group.delete()
            return redirect(return_path)
    else:
        return PermissionDenied()


def team_detail(request, profile_name, team_id):
    return_path = request.GET.get(
        'next',
        reverse('herders:teams', kwargs={'profile_name': profile_name})
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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

    return render(request, 'herders/profile/teams/team_detail.html', context)


@login_required
def team_edit(request, profile_name, team_id=None):
    return_path = reverse('herders:teams', kwargs={'profile_name': profile_name})
    if team_id:
        team = Team.objects.get(pk=team_id)
        edit_form = EditTeamForm(request.POST or None, instance=team)
    else:
        edit_form = EditTeamForm(request.POST or None)

    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    # Limit form choices to objects owned by the current user.
    edit_form.fields['group'].queryset = TeamGroup.objects.filter(owner=summoner)
    edit_form.fields['leader'].queryset = MonsterInstance.objects.filter(owner=summoner)
    edit_form.fields['roster'].queryset = MonsterInstance.objects.filter(owner=summoner)
    edit_form.helper.form_action = request.path + '?next=' + return_path

    context = {
        'profile_name': request.user.username,
        'return_path': return_path,
        'is_owner': is_owner,
        'view': 'teams',
    }

    if is_owner:
        if request.method == 'POST' and edit_form.is_valid():
            team = edit_form.save()
            messages.success(request, 'Saved changes to %s - %s.' % (team.group, team))

            return team_detail(request, profile_name, team.pk.hex)
    else:
        raise PermissionDenied()

    context['edit_team_form'] = edit_form
    return render(request, 'herders/profile/teams/team_edit.html', context)


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
        messages.success(request, 'Deleted team %s - %s.' % (team.group, team))
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


def bestiary(request):
    context = {
        'view': 'bestiary',
    }

    monster_list = cache.get('bestiary_data')

    if monster_list is None:
        monster_list = Monster.objects.select_related('awakens_from', 'awakens_to', 'leader_skill').filter(obtainable=True)
        cache.set('bestiary_data', monster_list, 900)

    context['monster_list'] = monster_list
    context['buff_list'] = MonsterSkillEffect.objects.filter(is_buff=True).exclude(icon_filename='').order_by('name')
    context['debuff_list'] = MonsterSkillEffect.objects.filter(is_buff=False).exclude(icon_filename='').order_by('name')
    context['other_effect_list'] = MonsterSkillEffect.objects.filter(icon_filename='').order_by('name')

    return render(request, 'herders/bestiary.html', context)


def bestiary_detail(request, monster_id):
    monster = get_object_or_404(Monster, pk=monster_id)
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

    return render(request, 'herders/bestiary_detail.html', context)


def bestiary_sanity_checks(request):
    from .models import MonsterSkill

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

            # Check  missing links resource
            if monster.can_awaken and monster.archetype != monster.TYPE_MATERIAL and (monster.summonerswar_co_url is None or monster.summonerswar_co_url == ''):
                monster_errors.append('Missing summonerswar.co link')

            if monster.wikia_url is None or monster.wikia_url == '':
                monster_errors.append('Missing wikia link')

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
