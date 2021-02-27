from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from bestiary.models import SkillEffect
from herders.decorators import username_case_redirect
from herders.forms import AddTeamGroupForm, EditTeamGroupForm, DeleteTeamGroupForm, EditTeamForm
from herders.models import Summoner, MonsterInstance, TeamGroup, Team


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
    if team.leader:
        effects = SkillEffect.objects.filter(
            pk__in=team.leader.monster.skills.exclude(effect=None).values_list('effect', flat=True)
        )

        for effect in effects:
            if effect not in team_effects:
                team_effects.append(effect)

    for team_member in team.roster.all():
        effects = SkillEffect.objects.filter(
            pk__in=team_member.monster.skills.exclude(effect=None).values_list('effect', flat=True)
        )
        for effect in effects:
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

