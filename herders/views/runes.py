from collections import OrderedDict

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.template import loader
from django.template.context_processors import csrf
from django.urls import reverse

from herders.decorators import username_case_redirect
from herders.filters import RuneInstanceFilter
from herders.forms import FilterRuneForm, \
    AddRuneInstanceForm, AssignRuneForm, AddRuneCraftInstanceForm
from herders.models import Summoner, MonsterInstance, RuneInstance, \
    RuneCraftInstance


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
    form = FilterRuneForm(request.GET or None)

    if form.is_valid():
        rune_filter = RuneInstanceFilter(form.cleaned_data, queryset=rune_queryset, summoner=summoner)
    else:
        rune_filter = RuneInstanceFilter(None, queryset=rune_queryset, summoner=summoner)

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
            monster = new_rune.assigned_to
            if monster:
                monster.default_build.runes.remove(* monster.default_build.runes.filter(slot=new_rune.slot))
                monster.default_build.runes.add(new_rune)

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
            monster = rune.assigned_to
            if monster:
                monster.default_build.runes.remove(*monster.default_build.runes.filter(slot=rune.slot))
                monster.default_build.runes.add(rune)
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

    monster.default_build.runes.remove(*monster.default_build.runes.filter(slot=rune.slot))
    monster.default_build.runes.add(rune)

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
        monster = rune.assigned_to
        rune.assigned_to = None
        rune.save()

        if monster:
            monster.default_build.runes.remove(rune)

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

        # Clear runes from Monster Default Build
        for mon in assigned_mons:
            mon.default_build.runes.clear()

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
        if mon:
            mon.default_build.runes.remove(rune)
            mon.rta_build.runes.remove(rune)
        messages.warning(request, 'Deleted ' + str(rune))
        rune.delete()

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

        for mon in assigned_mons:
            mon.default_build.clear()
            mon.rta_build.clear()

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
@login_required()
def rune_delete_notes_all(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        changed_notes = RuneInstance.objects.filter(owner=summoner, notes__isnull=False).update(notes=None)

        messages.success(request, 'Removed notes from ' + str(changed_notes) + ' rune(s).')

        response_data = {
            'code': 'success',
        }

        return JsonResponse(response_data)
    else:
        return HttpResponseForbidden()

