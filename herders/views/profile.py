"""
Profile CRUD, import/export, storage, and buildings
"""

import json

from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.mail import mail_admins
from django.db import IntegrityError
from django.db.models import FieldDoesNotExist
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.template import loader
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from herders.decorators import username_case_redirect
from herders.forms import RegisterUserForm, CrispyChangeUsernameForm, DeleteProfileForm, EditUserForm, \
    EditSummonerForm, EditBuildingForm, ImportPCAPForm, ImportSWParserJSONForm
from herders.models import Summoner, Storage, Building, BuildingInstance
from herders.profile_parser import parse_pcap, validate_sw_json
from herders.rune_optimizer_parser import export_win10
from herders.tasks import com2us_data_import


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
    form.helper.form_action = reverse(
        'herders:building_edit',
        kwargs={'profile_name': profile_name, 'building_id': building_id}
    )

    context = {
        'form': form,
    }
    context.update(csrf(request))

    if is_owner:
        if request.method == 'POST' and form.is_valid():
            owned_instance = form.save()
            messages.success(
                request,
                f'Updated {owned_instance.building.name} to level {owned_instance.level}'
            )

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

                        return render(
                            request,
                            'herders/profile/import_export/import_progress.html',
                            context={'profile_name': profile_name}
                        )

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

                    return render(
                        request,
                        'herders/profile/import_export/import_progress.html',
                        context={'profile_name': profile_name}
                    )
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
    response['Content-Disposition'] = f'attachment; filename={request.user.username}_swarfarm_win10_optimizer_export.json'

    return response
