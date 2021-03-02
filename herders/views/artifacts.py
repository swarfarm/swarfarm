from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.template.context_processors import csrf
from django.urls import reverse

from herders.decorators import username_case_redirect
from herders.filters import ArtifactInstanceFilter
from herders.forms import FilterArtifactForm, ArtifactInstanceForm, AssignArtifactForm
from herders.models import Summoner, MonsterInstance, ArtifactInstance, ArtifactCraftInstance


@username_case_redirect
def artifacts(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    filter_form = FilterArtifactForm(auto_id="filter_id_%s")
    filter_form.helper.form_action = reverse('herders:artifact_inventory', kwargs={'profile_name': profile_name})

    context = {
        'view': 'artifacts',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'filter_form': filter_form,
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/artifacts/base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
def inventory(request, profile_name, box_grouping=None):
    # If we passed in view mode or sort method, set the session variable and redirect back to base profile URL
    if box_grouping:
        request.session['artifact_inventory_box_method'] = box_grouping.lower()

    if request.session.modified:
        return HttpResponse("Artifact view mode cookie set")

    box_grouping = request.session.get('artifact_inventory_box_method', 'slot').lower()

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    artifact_queryset = ArtifactInstance.objects.filter(
        owner=summoner
    ).select_related(
        'assigned_to', 'assigned_to__monster'
    ).order_by('-quality', '-level')
    total_count = artifact_queryset.count()
    form = FilterArtifactForm(request.GET or None)

    if form.is_valid():
        artifact_filter = ArtifactInstanceFilter(form.cleaned_data, queryset=artifact_queryset)
    else:
        artifact_filter = ArtifactInstanceFilter(None, queryset=artifact_queryset)

    filtered_count = artifact_filter.qs.count()

    context = {
        'artifacts': artifact_filter.qs,
        'total_count': total_count,
        'filtered_count': filtered_count,
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        artifact_box = []
        if box_grouping == 'slot':
            # Element + archetype
            for slot_val, slot_desc in ArtifactInstance.NORMAL_ELEMENT_CHOICES:
                artifact_box.append({
                    'name': slot_desc,
                    'artifacts': artifact_filter.qs.filter(element=slot_val).order_by('main_stat', '-level')
                })
            for slot_val, slot_desc in ArtifactInstance.ARCHETYPE_CHOICES:
                artifact_box.append({
                    'name': slot_desc,
                    'artifacts': artifact_filter.qs.filter(archetype=slot_val).order_by('main_stat', '-level')
                })
        elif box_grouping == 'quality':
            for qual_val, qual_desc in reversed(ArtifactInstance.QUALITY_CHOICES):
                artifact_box.append({
                    'name': qual_desc,
                    'artifacts': artifact_filter.qs.filter(quality=qual_val)
                })
        elif box_grouping == 'orig. quality':
            for qual_val, qual_desc in reversed(ArtifactInstance.QUALITY_CHOICES):
                artifact_box.append({
                    'name': qual_desc,
                    'artifacts': artifact_filter.qs.filter(original_quality=qual_val)
                })
        elif box_grouping == 'equipped':
            artifact_box.append({
                'name': 'Not Equipped',
                'artifacts': artifact_filter.qs.filter(assigned_to__isnull=True)
            })

            # Create a dictionary of monster PKs and their equipped runes
            monsters = OrderedDict()
            unassigned_runes = artifact_filter.qs.filter(
                assigned_to__isnull=False
            ).select_related(
                'assigned_to',
                'assigned_to__monster'
            ).order_by(
                'assigned_to__monster__name',
                'slot'
            )

            for rune in unassigned_runes:
                if rune.assigned_to.pk not in monsters:
                    monsters[rune.assigned_to.pk] = {
                        'name': str(rune.assigned_to),
                        'artifacts': []
                    }

                monsters[rune.assigned_to.pk]['artifacts'].append(rune)
            for monster_runes in monsters.values():
                artifact_box.append(monster_runes)

        context['artifacts'] = artifact_box
        context['box_grouping'] = box_grouping
        return render(request, 'herders/profile/artifacts/inventory.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
@login_required
def add(request, profile_name):
    form = ArtifactInstanceForm(request.POST or None)
    form.helper.form_action = reverse('herders:artifact_add', kwargs={'profile_name': profile_name})
    template = loader.get_template('herders/profile/artifacts/form.html')

    if request.method == 'POST':
        if form.is_valid():
            # Create the rune instance
            new_artifact = form.save(commit=False)
            new_artifact.owner = request.user.summoner
            new_artifact.save()
            monster = new_artifact.assigned_to
            if monster:
                monster.default_build.artifacts.remove(*monster.default_build.artifacts.filter(slot=new_artifact.slot))
                monster.default_build.artifacts.add(new_artifact)

            messages.success(request, 'Added ' + str(new_artifact))

            # Send back blank form
            form = ArtifactInstanceForm()
            form.helper.form_action = reverse('herders:artifact_add', kwargs={'profile_name': profile_name})

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
        # Check for any pre-filled GET parameters
        element = request.GET.get('element', None)
        archetype = request.GET.get('archetype', None)
        if element is not None:
            slot = ArtifactInstance.SLOT_ELEMENTAL
        elif archetype is not None:
            slot = ArtifactInstance.SLOT_ARCHETYPE
        else:
            slot = None
        assigned_to = request.GET.get('assigned_to', None)

        try:
            assigned_monster = MonsterInstance.objects.get(owner=request.user.summoner, pk=assigned_to)
        except MonsterInstance.DoesNotExist:
            assigned_monster = None

        form = ArtifactInstanceForm(initial={
            'assigned_to': assigned_monster,
            'slot': slot,
            'element': element,
            'archetype': archetype,
        })
        form.helper.form_action = reverse('herders:artifact_add', kwargs={'profile_name': profile_name})

        # Return form filled in and errors shown
        context = {'form': form}
        context.update(csrf(request))

        response_data = {
            'html': template.render(context)
        }

    return JsonResponse(response_data)


@username_case_redirect
@login_required
def edit(request, profile_name, artifact_id):
    artifact = get_object_or_404(ArtifactInstance, pk=artifact_id)
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    form = ArtifactInstanceForm(request.POST or None, instance=artifact)
    form.helper.form_action = reverse('herders:artifact_edit', kwargs={'profile_name': profile_name, 'artifact_id': artifact_id})
    template = loader.get_template('herders/profile/artifacts/form.html')

    if is_owner:
        context = {'form': form}
        context.update(csrf(request))

        if request.method == 'POST' and form.is_valid():
            artifact = form.save()
            monster = artifact.assigned_to
            if monster:
                monster.default_build.artifacts.remove(*monster.default_build.artifacts.filter(slot=artifact.slot))
                monster.default_build.artifacts.add(artifact)
                
            messages.success(request, 'Saved changes to ' + str(artifact))
            form = ArtifactInstanceForm()
            form.helper.form_action = reverse('herders:artifact_edit', kwargs={'profile_name': profile_name, 'artifact_id': artifact_id})

            context = {'form': form}
            context.update(csrf(request))

            response_data = {
                'code': 'success',
                'html': template.render(context)
            }
        else:
            context = {'form': form}
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
def assign(request, profile_name, instance_id, slot=None):
    qs = ArtifactInstance.objects.filter(owner=request.user.summoner, assigned_to=None)
    filter_form = AssignArtifactForm(request.POST or None, initial={'slot': [slot]}, prefix='assign')
    filter_form.helper.form_action = reverse('herders:artifact_assign', kwargs={'profile_name': profile_name, 'instance_id': instance_id})
    # instance = get_object_or_404(MonsterInstance, pk=instance_id)
    # qs = qs.filter(Q(archetype=instance.monster.archetype) | Q(element=instance.monster.element))

    if request.method == 'POST' and filter_form.is_valid():
        filter = ArtifactInstanceFilter(filter_form.cleaned_data, queryset=qs)
        template = loader.get_template('herders/profile/artifacts/assign_results.html')

        context = {
            'filter': filter.qs,
            'profile_name': profile_name,
            'instance_id': instance_id,
        }
        context.update(csrf(request))

        response_data = {
            'code': 'results',
            'html': template.render(context)
        }
    else:
        filter = ArtifactInstanceFilter({'slot': [slot]}, queryset=qs)
        template = loader.get_template('herders/profile/artifacts/assign_form.html')

        context = {
            'filter': filter.qs,
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
def assign_choice(request, profile_name, instance_id, artifact_id):
    monster = get_object_or_404(MonsterInstance, pk=instance_id)
    artifact = get_object_or_404(ArtifactInstance, pk=artifact_id)

    # Clear existing artifacts assigned here
    monster.artifactinstance_set.filter(slot=artifact.slot).update(assigned_to=False)

    artifact.assigned_to = monster
    artifact.save()
    if monster:
        monster.default_build.artifacts.remove(*monster.default_build.artifacts.filter(slot=artifact.slot))
        monster.default_build.artifacts.add(artifact)

    response_data = {
        'code': 'success',
    }

    return JsonResponse(response_data)

@username_case_redirect
@login_required
def unassign(request, profile_name, artifact_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        artifact = get_object_or_404(ArtifactInstance, pk=artifact_id)
        monster = artifact.assigned_to
        artifact.assigned_to = None
        artifact.save()

        if monster:
            monster.default_build.artifacts.remove(artifact)

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def delete(request, profile_name, artifact_id):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        artifact = get_object_or_404(ArtifactInstance, pk=artifact_id)
        mon = artifact.assigned_to
        if mon:
            mon.default_build.artifacts.remove(artifact)
        artifact.delete()
        messages.warning(request, 'Deleted ' + str(artifact))

        if mon:
            mon.save()

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()
