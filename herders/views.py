from collections import OrderedDict
from copy import deepcopy

from django.http import Http404, HttpResponseForbidden, JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.forms.models import modelformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.template import loader, RequestContext
from bestiary.models import Monster, Fusion
from .forms import *
from .filters import *
from .models import Summoner, MonsterInstance, MonsterPiece, TeamGroup, Team


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
            messages.warning(request, 'Your profile has been permanently deleted.')
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
        messages.info(request, 'Now following %s' % new_follower.user.username)
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
        messages.info(request, 'Unfollowed %s' % removed_follower.user.username)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


def profile(request, profile_name=None):
    if profile_name is None:
        if request.user.is_authenticated():
            profile_name = request.user.username
        else:
            raise Http404('No user profile specified and not logged in.')

    summoner = get_object_or_404(Summoner, user__username=profile_name)

    # Determine if the person logged in is the one requesting the view
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)
    monster_filter_form = FilterMonsterInstanceForm()
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


def monster_inventory(request, profile_name, view_mode=None, box_grouping=None):
    # If we passed in view mode or sort method, set the session variable and redirect back to ourself without the view mode or box grouping
    if view_mode:
        request.session['profile_view_mode'] = view_mode.lower()

    if box_grouping:
        request.session['profile_group_method'] = box_grouping.lower()

    if request.session.modified:
        return HttpResponse("Profile view mode cookie set")

    view_mode = request.session.get('profile_view_mode', 'list').lower()
    box_grouping = request.session.get('profile_group_method', 'grade').lower()

    summoner = get_object_or_404(Summoner, user__username=profile_name)
    monster_queryset = MonsterInstance.committed.filter(owner=summoner)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if view_mode == 'list':
        monster_queryset = monster_queryset.select_related('monster', 'monster__leader_skill').prefetch_related(
            'monster__skills', 'monster__skills__skill_effect', 'runeinstance_set', 'team_set', 'team_leader')

    pieces = MonsterPiece.objects.filter(owner=summoner)

    form = FilterMonsterInstanceForm(request.POST or None)
    if form.is_valid():
        monster_filter = MonsterInstanceFilter(form.cleaned_data, queryset=monster_queryset)
    else:
        monster_filter = MonsterInstanceFilter(queryset=monster_queryset)

    context = {
        'monsters': monster_filter,
        'monster_pieces': pieces,
        'profile_name': profile_name,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        if view_mode == 'pieces':
            context['monster_pieces'] = MonsterPiece.committed.filter(owner=summoner)
            template = 'herders/profile/monster_inventory/summoning_pieces.html'
        elif view_mode == 'list':
            template = 'herders/profile/monster_inventory/list.html'
        else:
            # Group up the filtered monsters
            monster_stable = OrderedDict()

            if box_grouping == 'grade':
                monster_stable['6*'] = monster_filter.qs.filter(stars=6).order_by('-level', 'monster__element',
                                                                                  'monster__name')
                monster_stable['5*'] = monster_filter.qs.filter(stars=5).order_by('-level', 'monster__element',
                                                                                  'monster__name')
                monster_stable['4*'] = monster_filter.qs.filter(stars=4).order_by('-level', 'monster__element',
                                                                                  'monster__name')
                monster_stable['3*'] = monster_filter.qs.filter(stars=3).order_by('-level', 'monster__element',
                                                                                  'monster__name')
                monster_stable['2*'] = monster_filter.qs.filter(stars=2).order_by('-level', 'monster__element',
                                                                                  'monster__name')
                monster_stable['1*'] = monster_filter.qs.filter(stars=1).order_by('-level', 'monster__element',
                                                                                  'monster__name')
            elif box_grouping == 'level':
                monster_stable['40'] = monster_filter.qs.filter(level=40).order_by('-level', '-stars',
                                                                                   'monster__element', 'monster__name')
                monster_stable['39-31'] = monster_filter.qs.filter(level__gt=30).filter(level__lt=40).order_by('-level',
                                                                                                               '-stars',
                                                                                                               'monster__element',
                                                                                                               'monster__name')
                monster_stable['30-21'] = monster_filter.qs.filter(level__gt=20).filter(level__lte=30).order_by(
                    '-level', '-stars', 'monster__element', 'monster__name')
                monster_stable['20-11'] = monster_filter.qs.filter(level__gt=10).filter(level__lte=20).order_by(
                    '-level', '-stars', 'monster__element', 'monster__name')
                monster_stable['10-1'] = monster_filter.qs.filter(level__lte=10).order_by('-level', '-stars',
                                                                                          'monster__element',
                                                                                          'monster__name')
            elif box_grouping == 'attribute':
                monster_stable['water'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_WATER).order_by(
                    '-stars', '-level', 'monster__name')
                monster_stable['fire'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_FIRE).order_by(
                    '-stars', '-level', 'monster__name')
                monster_stable['wind'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_WIND).order_by(
                    '-stars', '-level', 'monster__name')
                monster_stable['light'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_LIGHT).order_by(
                    '-stars', '-level', 'monster__name')
                monster_stable['dark'] = monster_filter.qs.filter(monster__element=Monster.ELEMENT_DARK).order_by(
                    '-stars', '-level', 'monster__name')
            elif box_grouping == 'priority':
                monster_stable[MonsterInstance.PRIORITY_CHOICES[MonsterInstance.PRIORITY_HIGH][
                    1]] = MonsterInstance.committed.select_related('monster').filter(owner=summoner,
                                                                                     priority=MonsterInstance.PRIORITY_HIGH).order_by(
                    '-level', 'monster__element', 'monster__name')
                monster_stable[MonsterInstance.PRIORITY_CHOICES[MonsterInstance.PRIORITY_MED][
                    1]] = MonsterInstance.committed.select_related('monster').filter(owner=summoner,
                                                                                     priority=MonsterInstance.PRIORITY_MED).order_by(
                    '-level', 'monster__element', 'monster__name')
                monster_stable[MonsterInstance.PRIORITY_CHOICES[MonsterInstance.PRIORITY_LOW][
                    1]] = MonsterInstance.committed.select_related('monster').filter(owner=summoner,
                                                                                     priority=MonsterInstance.PRIORITY_LOW).order_by(
                    '-level', 'monster__element', 'monster__name')
                monster_stable[MonsterInstance.PRIORITY_CHOICES[MonsterInstance.PRIORITY_DONE][
                    1]] = MonsterInstance.committed.select_related('monster').filter(owner=summoner,
                                                                                     priority=MonsterInstance.PRIORITY_DONE).order_by(
                    '-level', 'monster__element', 'monster__name')
            else:
                raise Http404('Invalid sort method')

            context['monster_stable'] = monster_stable
            context['box_grouping'] = box_grouping
            template = 'herders/profile/monster_inventory/box.html'

        return render(request, template, context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


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

            messages.info(request, 'Your profile has been updated.')
            return redirect(return_path)
        else:
            return render(request, 'herders/profile/profile_edit.html', context)
    else:
        return HttpResponseForbidden()


@login_required
def profile_storage(request, profile_name):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if is_owner:
        form = EditEssenceStorageForm(request.POST or None, instance=request.user.summoner)
        form.helper.form_action = request.path
        template = loader.get_template('herders/essence_storage.html')

        if request.method == 'POST' and form.is_valid():
            form.save()
            messages.success(request, 'Updated essence storage.')

            response_data = {
                'code': 'success'
            }
        else:
            response_data = {
                'code': 'error',
                'html': template.render(RequestContext(request, {'form': form}))
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@login_required()
def monster_instance_add(request, profile_name):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if is_owner:
        if request.method == 'POST':
            form = AddMonsterInstanceForm(request.POST or None)
        else:
            form = AddMonsterInstanceForm(initial=request.GET.dict())

        form.helper.form_action = reverse('herders:monster_instance_add', kwargs={'profile_name': profile_name})

        template = loader.get_template('herders/profile/monster_inventory/add_monster_form.html')

        if request.method == 'POST' and form.is_valid():
            # Create the monster instance
            new_monster = form.save(commit=False)
            new_monster.owner = request.user.summoner
            new_monster.save()

            messages.success(request, 'Added %s to your collection.' % new_monster)

            response_data = {
                'code': 'success'
            }
        else:
            # Return form filled in and errors shown
            response_data = {
                'code': 'error',
                'html': template.render(RequestContext(request, {'add_monster_form': form}))
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


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
        new_monster = MonsterInstance.committed.create(owner=summoner, monster=monster_to_add, stars=int(stars),
                                                       level=int(level), fodder=True, notes='',
                                                       priority=MonsterInstance.PRIORITY_DONE)
        messages.success(request, 'Added %s to your collection.' % new_monster)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@login_required()
def monster_instance_bulk_add(request, profile_name):
    return_path = reverse('herders:profile_default', kwargs={'profile_name': profile_name})
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    BulkAddFormset = modelformset_factory(MonsterInstance, form=BulkAddMonsterInstanceForm,
                                          formset=BulkAddMonsterInstanceFormset, extra=5, max_num=50)

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


def monster_instance_view(request, profile_name, instance_id):
    return_path = request.GET.get(
        'next',
        request.path
    )
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    try:
        instance = MonsterInstance.committed.select_related('monster', 'monster__leader_skill').prefetch_related(
            'monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        raise Http404()

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'return_path': return_path,
        'instance': instance,
        'is_owner': is_owner,
        'view': 'profile',
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/monster_view/base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html')


def monster_instance_view_sidebar(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.committed.select_related('monster').get(pk=instance_id)
    except ObjectDoesNotExist:
        raise Http404()

    context = {
        'instance': instance,
    }

    return render(request, 'herders/profile/monster_view/side_info.html', context)


def monster_instance_view_runes(request, profile_name, instance_id):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    try:
        instance = MonsterInstance.committed.select_related('monster', 'monster__leader_skill').prefetch_related(
            'monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        raise Http404()

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
        'is_owner': is_owner,
    }

    return render(request, 'herders/profile/monster_view/runes.html', context)


def monster_instance_view_stats(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.committed.select_related('monster', 'monster__leader_skill').prefetch_related(
            'monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        raise Http404()

    context = {
        'instance': instance,
    }

    return render(request, 'herders/profile/monster_view/stats.html', context)


def monster_instance_view_skills(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.committed.select_related('monster', 'monster__leader_skill').prefetch_related(
            'monster__skills').get(pk=instance_id)
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
        'instance': instance,
        'skills': skills,
    }

    return render(request, 'herders/profile/monster_view/skills.html', context)


def monster_instance_view_info(request, profile_name, instance_id):
    try:
        instance = MonsterInstance.committed.select_related('monster', 'monster__leader_skill').prefetch_related(
            'monster__skills').get(pk=instance_id)
    except ObjectDoesNotExist:
        raise Http404()

    context = {
        'instance': instance,
        'profile_name': profile_name,
    }

    return render(request, 'herders/profile/monster_view/notes_info.html', context)


@login_required()
def monster_instance_edit(request, profile_name, instance_id):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    instance = get_object_or_404(MonsterInstance, pk=instance_id)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)
    template = loader.get_template('herders/profile/monster_view/edit_form.html')

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

        if not instance.monster.fusion_food:
            form.helper['ignore_for_fusion'].wrap(Div, css_class="hidden")

        if request.method == 'POST' and form.is_valid():
            form.save()

            response_data = {
                'code': 'success'
            }
        else:
            # Return form filled in and errors shown
            response_data = {
                'code': 'error',
                'html': template.render(RequestContext(request, {'edit_monster_form': form}))
            }

        return JsonResponse(response_data)
    else:
        raise PermissionDenied()


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
        return HttpResponseForbidden()


@login_required()
def monster_instance_power_up(request, profile_name, instance_id):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)
    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    template = loader.get_template('herders/profile/monster_view/power_up_form.html')

    form = PowerUpMonsterInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:monster_instance_power_up',
                                      kwargs={'profile_name': profile_name, 'instance_id': instance_id})

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
                        validation_errors[
                            'base_monster_level'] = "%s is not at max level for the current star rating (Lvl %s)." % (
                        monster.monster.name, monster.monster.max_level_from_stars())

                    # Check number of fodder monsters
                    if len(food_monsters) < monster.stars:
                        validation_errors[
                            'food_monster_quantity'] = "Evolution requres %s food monsters." % monster.stars

                    # Check fodder star ratings - must be same as monster
                    for food in food_monsters:
                        if food.stars != monster.stars:
                            if 'food_monster_stars' not in validation_errors:
                                validation_errors[
                                    'food_monster_stars'] = "All food monsters must be %s stars or higher." % monster.stars

                # Perform the stars++ if no errors
                if not validation_errors:
                    # Level up stars
                    monster.stars += 1
                    monster.level = 1
                    monster.save()
                    messages.success(request,
                                     'Successfully evolved %s to %s<span class="glyphicon glyphicon-star"></span>' % (
                                     monster.monster.name, monster.stars), extra_tags='safe')

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

    # Any errors in the form will fall through to here and be displayed
    context['validation_errors'] = validation_errors
    response_data['html'] = template.render(RequestContext(request, context))

    return JsonResponse(response_data)


@login_required()
def monster_instance_awaken(request, profile_name, instance_id):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    template = loader.get_template('herders/profile/monster_view/awaken_form.html')

    form = AwakenMonsterInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:monster_instance_awaken',
                                      kwargs={'profile_name': profile_name, 'instance_id': instance_id})

    if is_owner:
        if not monster.monster.is_awakened:
            if request.method == 'POST' and form.is_valid():
                # Subtract essences from inventory if requested
                if form.cleaned_data['subtract_materials']:
                    summoner = Summoner.objects.get(user=request.user)

                    summoner.storage_magic_high -= monster.monster.awaken_mats_magic_high
                    summoner.storage_magic_mid -= monster.monster.awaken_mats_magic_mid
                    summoner.storage_magic_low -= monster.monster.awaken_mats_magic_low
                    summoner.storage_fire_high -= monster.monster.awaken_mats_fire_high
                    summoner.storage_fire_mid -= monster.monster.awaken_mats_fire_mid
                    summoner.storage_fire_low -= monster.monster.awaken_mats_fire_low
                    summoner.storage_water_high -= monster.monster.awaken_mats_water_high
                    summoner.storage_water_mid -= monster.monster.awaken_mats_water_mid
                    summoner.storage_water_low -= monster.monster.awaken_mats_water_low
                    summoner.storage_wind_high -= monster.monster.awaken_mats_wind_high
                    summoner.storage_wind_mid -= monster.monster.awaken_mats_wind_mid
                    summoner.storage_wind_low -= monster.monster.awaken_mats_wind_low
                    summoner.storage_dark_high -= monster.monster.awaken_mats_dark_high
                    summoner.storage_dark_mid -= monster.monster.awaken_mats_dark_mid
                    summoner.storage_dark_low -= monster.monster.awaken_mats_dark_low
                    summoner.storage_light_high -= monster.monster.awaken_mats_light_high
                    summoner.storage_light_mid -= monster.monster.awaken_mats_light_mid
                    summoner.storage_light_low -= monster.monster.awaken_mats_light_low

                    summoner.save()

                # Perform the awakening by instance's monster source ID
                monster.monster = monster.monster.awakens_to
                monster.save()

                response_data = {
                    'code': 'success',
                    'removeElement': '#awakenMonsterButton',
                }

            else:
                storage = summoner.get_storage()
                available_essences = OrderedDict()

                for element, essences in monster.monster.get_awakening_materials().iteritems():
                    available_essences[element] = OrderedDict()
                    for size, cost in essences.iteritems():
                        if cost > 0:
                            available_essences[element][size] = {
                                'qty': storage[element][size],
                                'sufficient': storage[element][size] >= cost,
                            }

                response_data = {
                    'code': 'error',
                    'html': template.render(RequestContext(request, {
                        'awaken_form': form,
                        'available_essences': available_essences,
                        'instance': monster,
                    }))
                }
        else:
            error_template = loader.get_template('herders/profile/monster_already_awakened.html')
            response_data = {
                'code': 'error',
                'html': error_template.render(RequestContext(request, {}))
            }

        return JsonResponse(response_data)
    else:
        raise PermissionDenied()


@login_required()
def monster_instance_duplicate(request, profile_name, instance_id):
    monster = get_object_or_404(MonsterInstance, pk=instance_id)

    # Check for proper owner before copying
    if request.user.summoner == monster.owner:
        newmonster = monster
        newmonster.pk = None
        newmonster.save()
        messages.success(request, 'Succesfully copied ' + str(newmonster))

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@login_required()
def monster_piece_add(request, profile_name):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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
            response_data = {
                'code': 'error',
                'html': template.render(RequestContext(request, {'form': form}))
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@login_required()
def monster_piece_edit(request, profile_name, instance_id):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    pieces = get_object_or_404(MonsterPiece, pk=instance_id)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)
    template = loader.get_template('herders/profile/monster_inventory/monster_piece_form.html')

    if is_owner:
        form = MonsterPieceForm(request.POST or None, instance=pieces)
        form.helper.form_action = request.path

        if request.method == 'POST' and form.is_valid():
            form.save()

            response_data = {
                'code': 'success'
            }
        else:
            # Return form filled in and errors shown
            response_data = {
                'code': 'error',
                'html': template.render(RequestContext(request, {'form': form}))
            }

        return JsonResponse(response_data)
    else:
        raise PermissionDenied()


@login_required()
def monster_piece_summon(request, profile_name, instance_id):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    pieces = get_object_or_404(MonsterPiece, pk=instance_id)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if is_owner:
        if pieces.can_summon():
            new_monster = MonsterInstance.committed.create(owner=summoner, monster=pieces.monster,
                                                           stars=pieces.monster.base_stars, level=1, fodder=False,
                                                           notes='', priority=MonsterInstance.PRIORITY_DONE)
            messages.success(request, 'Added %s to your collection.' % new_monster)

            # Remove the pieces, delete if 0
            pieces.pieces -= pieces.PIECE_REQUIREMENTS[pieces.monster.base_stars]
            pieces.save()

            if pieces.pieces <= 0:
                pieces.delete()

            response_data = {
                'code': 'success'
            }

            return JsonResponse(response_data)
    else:
        raise PermissionDenied()


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
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)
    fusions = Fusion.objects.all()

    context = {
        'view': 'fusion',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'fusions': fusions,
    }

    return render(request, 'herders/profile/fusion/base.html', context)


def fusion_progress_detail(request, profile_name, monster_slug):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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
            return Http404()
        else:
            level = 10 + fusion.stars * 5
            ingredients = []

            # Check if fusion has been completed already
            fusion_complete = MonsterInstance.committed.filter(
                Q(owner=summoner), Q(monster=fusion.product) | Q(monster=fusion.product.awakens_to)
            ).exists()

            # Scan summoner's collection for instances each ingredient
            fusion_ready = True

            for ingredient in fusion.ingredients.all().select_related('awakens_from', 'awakens_to'):
                owned_ingredients = MonsterInstance.committed.filter(
                    Q(owner=summoner),
                    Q(monster=ingredient) | Q(monster=ingredient.awakens_from),
                ).order_by('-stars', '-level', '-monster__is_awakened')

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

                if not complete:
                    fusion_ready = False

                # Check if this ingredient is fusable
                if not acquired:
                    try:
                        sub_fusion = Fusion.objects.get(product=ingredient.awakens_from)
                    except Fusion.DoesNotExist:
                        sub_fusion_awakening_cost = None
                    else:
                        awakened_sub_fusion_ingredients = MonsterInstance.committed.filter(
                            monster__pk__in=sub_fusion.ingredients.values_list('pk', flat=True),
                            ignore_for_fusion=False,
                            owner=summoner,
                        )
                        sub_fusion_awakening_cost = sub_fusion.total_awakening_cost(awakened_sub_fusion_ingredients)
                else:
                    sub_fusion_awakening_cost = None

                ingredient_progress = {
                    'instance': ingredient,
                    'owned': owned_ingredients,
                    'complete': complete,
                    'acquired': acquired,
                    'evolved': evolved,
                    'leveled': leveled,
                    'awakened': awakened,
                    'sub_fusion_cost': sub_fusion_awakening_cost,
                }
                ingredients.append(ingredient_progress)

            awakened_owned_ingredients = MonsterInstance.committed.filter(
                monster__pk__in=fusion.ingredients.values_list('pk', flat=True),
                ignore_for_fusion=False,
                owner=summoner,
            )
            total_cost = fusion.total_awakening_cost(awakened_owned_ingredients)
            essences_satisfied, total_missing = fusion.missing_awakening_cost(summoner)

            # Determine the total/missing essences including sub-fusions
            if fusion.sub_fusion_available():
                total_sub_fusion_cost = deepcopy(total_cost)
                for ingredient in ingredients:
                    if ingredient['sub_fusion_cost']:
                        for element, sizes in total_sub_fusion_cost.iteritems():
                            for size, qty in sizes.iteritems():
                                total_sub_fusion_cost[element][size] += ingredient['sub_fusion_cost'][element][size]

                # Now determine what's missing based on owner's storage
                storage = summoner.get_storage()

                sub_fusion_total_missing = {
                    element: {
                        size: total_sub_fusion_cost[element][size] - storage[element][size] if total_sub_fusion_cost[element][size] > storage[element][size] else 0
                        for size, qty in element_sizes.items()
                    }
                    for element, element_sizes in total_sub_fusion_cost.items()
                }

                sub_fusion_mats_satisfied = True
                for sizes in total_sub_fusion_cost.itervalues():
                    for qty in sizes.itervalues():
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
            messages.warning(request, 'Deleted team group %s' % team_group.name)
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

    if is_owner or summoner.public:
        return render(request, 'herders/profile/teams/team_detail.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


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
    edit_form.fields['leader'].queryset = MonsterInstance.committed.filter(owner=summoner)
    edit_form.fields['roster'].queryset = MonsterInstance.committed.filter(owner=summoner)
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
        messages.warning(request, 'Deleted team %s - %s.' % (team.group, team))
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


def runes(request, profile_name):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    filter_form = FilterRuneForm(auto_id="filter_id_%s")
    filter_form.helper.form_action = reverse('herders:rune_inventory', kwargs={'profile_name': profile_name})

    context = {
        'view': 'runes',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'rune_filter_form': filter_form,
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/runes/base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


def rune_inventory(request, profile_name, view_mode=None, box_grouping=None):
    # If we passed in view mode or sort method, set the session variable and redirect back to base profile URL
    if view_mode:
        request.session['rune_inventory_view_mode'] = view_mode.lower()

    if box_grouping:
        request.session['rune_inventory_box_method'] = box_grouping.lower()

    if request.session.modified:
        return HttpResponse("Rune view mode cookie set")

    summoner = get_object_or_404(Summoner, user__username=profile_name)
    rune_queryset = RuneInstance.committed.filter(owner=summoner)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    form = FilterRuneForm(request.POST or None)
    view_mode = request.session.get('rune_inventory_view_mode', 'box').lower()
    box_grouping = request.session.get('rune_inventory_box_method', 'slot').lower()

    if form.is_valid():
        rune_filter = RuneInstanceFilter(form.cleaned_data, queryset=rune_queryset)
    else:
        rune_filter = RuneInstanceFilter(None, queryset=rune_queryset)

    context = {
        'runes': rune_filter,
        'profile_name': profile_name,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        if view_mode == 'box':
            rune_box = OrderedDict()
            if box_grouping == 'slot':
                rune_box['Slot 1'] = rune_filter.qs.filter(slot=1)
                rune_box['Slot 2'] = rune_filter.qs.filter(slot=2)
                rune_box['Slot 3'] = rune_filter.qs.filter(slot=3)
                rune_box['Slot 4'] = rune_filter.qs.filter(slot=4)
                rune_box['Slot 5'] = rune_filter.qs.filter(slot=5)
                rune_box['Slot 6'] = rune_filter.qs.filter(slot=6)
            elif box_grouping == 'grade':
                rune_box['6*'] = rune_filter.qs.filter(stars=6)
                rune_box['5*'] = rune_filter.qs.filter(stars=5)
                rune_box['4*'] = rune_filter.qs.filter(stars=4)
                rune_box['3*'] = rune_filter.qs.filter(stars=3)
                rune_box['2*'] = rune_filter.qs.filter(stars=2)
                rune_box['1*'] = rune_filter.qs.filter(stars=1)
            elif box_grouping == 'equipped':
                rune_box['Not Equipped'] = rune_filter.qs.filter(assigned_to__isnull=True)
                rune_box['Equipped'] = rune_filter.qs.filter(assigned_to__isnull=False)
            elif box_grouping == 'type':
                for (type, type_name) in RuneInstance.TYPE_CHOICES:
                    rune_box[type_name] = rune_filter.qs.filter(type=type)

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


def rune_counts(request, profile_name):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if is_owner:
        response_data = {
            'code': 'success',
            'counts': summoner.get_rune_counts()
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@login_required
def rune_add(request, profile_name):
    form = AddRuneInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:rune_add', kwargs={'profile_name': profile_name})
    template = loader.get_template('herders/profile/runes/add_form.html')

    if request.method == 'POST':
        if form.is_valid():
            # Create the monster instance
            new_rune = form.save(commit=False)
            new_rune.owner = request.user.summoner
            new_rune.save()

            messages.success(request, 'Added ' + str(new_rune))

            # Send back blank form
            form = AddRuneInstanceForm()
            form.helper.form_action = reverse('herders:rune_add', kwargs={'profile_name': profile_name})

            response_data = {
                'code': 'success',
                'html': template.render(RequestContext(request, {'add_rune_form': form}))
            }
        else:
            response_data = {
                'code': 'error',
                'html': template.render(RequestContext(request, {'add_rune_form': form}))
            }
    else:
        # Check for any pre-filled GET parameters
        slot = request.GET.get('slot', None)
        assigned_to = request.GET.get('assigned_to', None)

        form = AddRuneInstanceForm(initial={
            'assigned_to': assigned_to,
            'slot': slot if slot is not None else 1,
        })
        form.helper.form_action = reverse('herders:rune_add', kwargs={'profile_name': profile_name})

        # Return form filled in and errors shown
        response_data = {
            'html': template.render(RequestContext(request, {'add_rune_form': form}))
        }

    return JsonResponse(response_data)


@login_required
def rune_edit(request, profile_name, rune_id):
    rune = get_object_or_404(RuneInstance, pk=rune_id)
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    form = AddRuneInstanceForm(request.POST or None, instance=rune, auto_id='edit_id_%s')
    form.helper.form_action = reverse('herders:rune_edit', kwargs={'profile_name': profile_name, 'rune_id': rune_id})
    template = loader.get_template('herders/profile/runes/add_form.html')

    if is_owner:
        if request.method == 'POST' and form.is_valid():
            rune = form.save()
            messages.success(request, 'Saved changes to ' + str(rune))
            form = AddRuneInstanceForm(auto_id='edit_id_%s')
            form.helper.form_action = reverse('herders:rune_edit',
                                              kwargs={'profile_name': profile_name, 'rune_id': rune_id})

            response_data = {
                'code': 'success',
                'html': template.render(RequestContext(request, {'add_rune_form': form}))
            }
        else:
            # Return form filled in and errors shown
            response_data = {
                'code': 'error',
                'html': template.render(RequestContext(request, {'add_rune_form': form}))
            }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@login_required
def rune_assign(request, profile_name, instance_id, slot=None):
    rune_queryset = RuneInstance.committed.filter(owner=request.user.summoner, assigned_to=None)
    filter_form = AssignRuneForm(request.POST or None, initial={'slot': slot})
    filter_form.helper.form_action = reverse('herders:rune_assign',
                                             kwargs={'profile_name': profile_name, 'instance_id': instance_id})

    if slot:
        rune_queryset = rune_queryset.filter(slot=slot)

    rune_filter = RuneInstanceFilter(request.POST, queryset=rune_queryset)

    if request.method == 'POST':
        template = loader.get_template('herders/profile/runes/assign_results.html')

        response_data = {
            'code': 'results',
            'html': template.render(RequestContext(request, {
                'filter': rune_filter,
                'profile_name': profile_name,
                'instance_id': instance_id,
            }))
        }
    else:
        template = loader.get_template('herders/profile/runes/assign_form.html')

        response_data = {
            'code': 'success',
            'html': template.render(RequestContext(request, {
                'filter': rune_filter,
                'form': filter_form,
                'profile_name': profile_name,
                'instance_id': instance_id,
            }))
        }

    return JsonResponse(response_data)


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


@login_required
def rune_unassign(request, profile_name, rune_id):
    rune = get_object_or_404(RuneInstance, pk=rune_id)
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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


@login_required
def rune_delete(request, profile_name, rune_id):
    rune = get_object_or_404(RuneInstance, pk=rune_id)
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

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


@login_required
def rune_delete_all(request, profile_name):
    summoner = get_object_or_404(Summoner, user__username=profile_name)
    is_owner = (request.user.is_authenticated() and summoner.user == request.user)

    if is_owner:
        death_row = RuneInstance.committed.filter(owner=summoner)
        number_killed = death_row.count()
        assigned_mons = []
        for rune in death_row:
            if rune.assigned_to and rune.assigned_to not in assigned_mons:
                assigned_mons.append(rune.assigned_to)

        death_row.delete()
        messages.warning(request, 'Deleted ' + str(number_killed) + ' rune(s).')

        for mon in assigned_mons:
            mon.save()

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()
