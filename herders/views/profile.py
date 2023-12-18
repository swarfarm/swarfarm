"""
Profile CRUD, import/export, storage
"""

import json
import copy

from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.core.mail import mail_admins
from django.db import IntegrityError
from django.db.models.aggregates import Avg, Count, Max, Min, StdDev, Sum
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.template import loader
from django.template.context_processors import csrf
from django.utils.html import mark_safe
from django.utils.text import slugify

from herders.decorators import username_case_redirect
from herders.forms import RegisterUserForm, CrispyChangeUsernameForm, DeleteProfileForm, EditUserForm, \
    EditSummonerForm, ImportSWParserJSONForm
from herders.models import ArtifactInstance, MonsterInstance, RuneCraftInstance, RuneInstance, Summoner, MaterialStorage, MonsterShrineStorage, ArtifactCraftInstance
from herders.profile_parser import validate_sw_json
from herders.rune_optimizer_parser import export_win10
from herders.tasks import com2us_data_import
from herders.views.compare import _get_efficiency_statistics

from bestiary.models import GameItem, RuneCraft, Rune, Artifact, Monster, Fusion


def register(request):
    form = RegisterUserForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            if User.objects.filter(username__iexact=form.cleaned_data['username']).exists():
                form.add_error('username', 'Username already taken')
            elif User.objects.filter(email__iexact=form.cleaned_data['email']).exists():
                form.add_error(
                    'email',
                    mark_safe(
                        f'Email already in use. You can <a href="{reverse("password_reset")}">reset your password if you forgot it</a>.'
                    )
                )
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
                        dark_mode=form.cleaned_data['dark_mode'],
                        consent_report=form.cleaned_data['consent_report'],
                        consent_top=form.cleaned_data['consent_top'],
                    )
                    new_summoner.save()

                    # Automatically log them in
                    user = authenticate(
                        username=form.cleaned_data['username'], password=form.cleaned_data['password'])
                    if user is not None:
                        if user.is_active:
                            login(request, user)
                            return redirect('herders:profile_default', profile_name=user.username)
                except IntegrityError as e:
                    if new_user is not None:
                        new_user.delete()
                    if new_summoner is not None:
                        new_summoner.delete()

                    form.add_error(
                        None, 'There was an issue completing your registration. Please try again.')
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
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    form = DeleteProfileForm(request.POST or None)
    form.helper.form_action = reverse('herders:profile_delete', kwargs={
                                      'profile_name': profile_name})

    context = {
        'form': form,
    }
    if is_owner:
        if request.method == 'POST' and form.is_valid():
            logout(request)
            user.delete()
            messages.warning(
                request, 'Your profile has been permanently deleted.')
            return redirect('news:latest_news')

        return render(request, 'herders/profile/profile_delete.html', context)
    else:
        return HttpResponseForbidden("You don't own this profile")


@username_case_redirect
@login_required
def following(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_following', kwargs={
                'profile_name': profile_name})
    )

    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    followed_by = {f.pk: f for f in summoner.followed_by.all()}
    friends = {
        f.pk: {
            'obj': f,
            'following': True,
            'followed_by': False,
        } for f in summoner.following.all()
    }

    for f_pk, f_obj in followed_by.items():
        if f_pk in friends:
            friends[f_pk]['followed_by'] = True
        else:
            friends[f_pk] = {
                'obj': f_obj,
                'following': False,
                'followed_by': True,
            }

    friends = sorted(list(friends.values()), key=lambda el: (-el['following'], -el['followed_by']))

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'summoner': summoner,
        'friends': friends,
        'view': 'following',
        'return_path': return_path,
    }

    return render(request, 'herders/profile/following/list.html', context)


@username_case_redirect
@login_required
def follow_add(request, profile_name, follow_username):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={
                'profile_name': profile_name})
    )

    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
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
        reverse('herders:profile_default', kwargs={
                'profile_name': profile_name})
    )

    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()
    removed_follower = get_object_or_404(
        Summoner, user__username=follow_username)
    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        summoner.following.remove(removed_follower)
        messages.info(request, 'Unfollowed %s' %
                      removed_follower.user.username)
        return redirect(return_path)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def profile_edit(request, profile_name):
    return_path = request.GET.get(
        'next',
        reverse('herders:profile_default', kwargs={
                'profile_name': profile_name})
    )
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    user_form = EditUserForm(request.POST or None, instance=request.user)
    summoner_form = EditSummonerForm(
        request.POST or None, instance=request.user.summoner)

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
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if is_owner:
        craft_mats = []
        monster_mats = []
        monster_shrine_mats = []
        summoner_material_storage = {
            ms.item.com2us_id: ms for ms in MaterialStorage.objects.select_related('item').filter(owner=summoner)}

        essences = {gi.com2us_id: gi for gi in GameItem.objects.filter(
            category=GameItem.CATEGORY_ESSENCE)}
        essence_elements = {
            key: {
                'name': None,
                'field_name': None,
                'element': None,
                'qty': [0, 0, 0],
            } for key in ['magic', 'fire', 'water', 'wind', 'light', 'dark']
        }
        essence_lvl = ['low', 'mid', 'high']

        for key, essence in essences.items():
            slug_split = essence.slug.split('-')
            element = slug_split[0]
            if not essence_elements[element]['name']:
                essence_elements[element]['name'] = ' '.join(
                    essence.name.split(' ')[::2])  # drop `low`, `mid`, `high`
            if not essence_elements[element]['field_name']:
                essence_elements[element]['field_name'] = '_'.join(
                    slug_split[::2])  # drop `low`, `mid`, `high`, connect with `_`
            if not essence_elements[element]['element']:
                essence_elements[element]['element'] = element  # only element

            essence_elements[element]['qty'][essence_lvl.index(
                slug_split[1])] = summoner_material_storage[key].quantity if key in summoner_material_storage else 0
        essence_mats = list(essence_elements.values())

        craft_categories = [
            GameItem.CATEGORY_CRAFT_STUFF,
            GameItem.CATEGORY_RUNE_CRAFT,
            GameItem.CATEGORY_ARTIFACT_CRAFT,
        ]
        crafts = {gi.com2us_id: gi for gi in GameItem.objects.filter(
            category__in=craft_categories).order_by('com2us_id')}
        for key, craft in crafts.items():
            craft_mats.append({
                'name': craft.name,
                'field_name': craft.slug.replace('-', '_'),
                'qty': summoner_material_storage[key].quantity if key in summoner_material_storage else 0,
            })

        material_monsters = {gi.com2us_id: gi for gi in GameItem.objects.filter(
            category=GameItem.CATEGORY_MATERIAL_MONSTER).order_by('category')}
        for key, material_monster in material_monsters.items():
            monster_mats.append({
                'name': material_monster.name.replace('White', 'Light').replace('Red', 'Fire').replace('Blue', 'Water').replace('Gold', 'Wind'),
                'field_name': material_monster.slug.replace('-', '_').replace('white', 'light').replace('red', 'fire').replace('blue', 'water').replace('gold', 'wind'),
                'qty': summoner_material_storage[key].quantity if key in summoner_material_storage else 0,
            })

        # Monster Shrine, may be moved to other page
        for monster_shrine in MonsterShrineStorage.objects.select_related('item').filter(owner=summoner).order_by('item__awaken_level', 'item__name'):
            monster_shrine_mats.append({
                'name': monster_shrine.item.name,
                'img': monster_shrine.item.image_filename,
                'field_name': f'shrine_{monster_shrine.item.com2us_id}',
                'qty': monster_shrine.quantity,
            })

        context = {
            'is_owner': is_owner,
            'profile_name': profile_name,
            'summoner': summoner,
            'essence_mats': essence_mats,
            'craft_mats': craft_mats,
            'monster_mats': monster_mats,
            'monster_shrine_mats': monster_shrine_mats,
        }

        return render(request, 'herders/profile/storage/base.html', context=context)
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def storage_update(request, profile_name):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
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
            field_name, essence_size = field_name.split('.')

        field_name = field_name.split('_')
        if essence_size:
            field_name.insert(1, essence_size)
        field_name = '-'.join(field_name)  # slug

        if 'angelmon' in field_name:
            field_name = field_name.replace('light', 'white').replace(
                'fire', 'red').replace('water', 'blue').replace('wind', 'gold')

        try:
            item = MaterialStorage.objects.select_related(
                'item').get(owner=summoner, item__slug=field_name)
            item.quantity = new_value
            item.save()
        except MaterialStorage.DoesNotExist:
            # ignore some strange 'UNKNOWN ITEM'
            game_item = GameItem.objects.get(slug=field_name)
            item = MaterialStorage.objects.create(
                owner=summoner, item=game_item, quantity=new_value)
            item.save()
        except GameItem.DoesNotExist:
            return HttpResponseBadRequest('No such item exists')

        return HttpResponse()
    else:
        return HttpResponseForbidden()


@username_case_redirect
@login_required
def import_export_home(request, profile_name):
    return render(request, 'herders/profile/import_export/base.html', context={
        'profile_name': profile_name,
        'view': 'importexport'
    })


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
        form.helper.form_action = reverse('herders:import_swparser', kwargs={
                                          'profile_name': profile_name})

        if form.is_valid():
            summoner = get_object_or_404(
                Summoner, user__username=request.user.username)
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
                schema_errors, validation_errors = validate_sw_json(
                    data, request.user.summoner)

                if schema_errors:
                    errors.append(schema_errors)

                if validation_errors:
                    validation_failures += validation_errors

                if not errors and (not validation_failures or import_options['ignore_validation_errors']):
                    # Queue the import
                    task = com2us_data_import.delay(
                        data, summoner.pk, import_options)
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


def _get_stats_summary(summoner):
    report = {
        "runes": {},
        "artifacts": {},
        "monsters": {
            'Count': MonsterInstance.objects.filter(owner=summoner).count() + (MonsterShrineStorage.objects.filter(owner=summoner).aggregate(count=Sum('quantity'))['count'] or 0),
            'Nat 5⭐': MonsterInstance.objects.filter(owner=summoner, monster__natural_stars=5).count(),
            'Nat 4⭐': MonsterInstance.objects.filter(owner=summoner, monster__natural_stars=4).count(),
        },
    }
    runes_summoner_eff = _get_efficiency_statistics(
        RuneInstance, summoner, count=True, worth=True)
    for key in runes_summoner_eff.keys():
        report["runes"][key] = runes_summoner_eff[key]

    artifacts_summoner_eff = _get_efficiency_statistics(
        ArtifactInstance, summoner, count=True)
    for key in artifacts_summoner_eff.keys():
        report["artifacts"][key] = artifacts_summoner_eff[key]

    monsters_shrine = MonsterShrineStorage.objects.select_related(
        'owner', 'item').filter(owner=summoner, item__natural_stars__gte=4)
    for monster in monsters_shrine:
        report['monsters'][f'Nat {monster.item.natural_stars}⭐'] += monster.quantity or 0

    return report


@username_case_redirect
@login_required
def stats(request, profile_name):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'stats': _get_stats_summary(summoner),
        'view': 'stats',
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES},
    }

    return render(request, 'herders/profile/stats/summary.html', context)


def _get_stats_runes(summoner):
    stats = {stat[1]: 0 for stat in sorted(
        Rune.STAT_CHOICES, key=lambda x: x[1])}
    qualities = {quality[1]: 0 for quality in Rune.QUALITY_CHOICES}
    qualities[None] = 0
    report_runes = {
        'summary': {
            'Count': 0,
            'Worth': 0,
        },
        'stars': {
            6: 0,
            5: 0,
            4: 0,
            3: 0,
            2: 0,
            1: 0,
        },
        'sets': {rune_set[1]: 0 for rune_set in sorted(Rune.TYPE_CHOICES, key=lambda x: x[1])},
        'quality': copy.deepcopy(qualities),
        'quality_original': copy.deepcopy(qualities),
        'slot': {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        },
        'main_stat': copy.deepcopy(stats),
        'innate_stat': copy.deepcopy(stats),
        'substats': copy.deepcopy(stats),
    }
    report_runes['innate_stat'][None] = 0
    runes = RuneInstance.objects.select_related('owner').filter(owner=summoner)

    rune_substats = dict(Rune.STAT_CHOICES)

    report_runes['summary']['Count'] = runes.count()
    for rune in runes:
        for sub_stat in rune.substats:
            report_runes['substats'][rune_substats[sub_stat]] += 1

        report_runes['stars'][rune.stars] += 1
        report_runes['sets'][rune.get_type_display()] += 1
        report_runes['quality'][rune.get_quality_display()] += 1
        report_runes['quality_original'][rune.get_original_quality_display()] += 1
        report_runes['slot'][rune.slot] += 1
        report_runes['main_stat'][rune.get_main_stat_display()] += 1
        report_runes['innate_stat'][rune.get_innate_stat_display()] += 1
        report_runes['summary']['Worth'] += rune.value or 0

    summoner_eff = _get_efficiency_statistics(RuneInstance, summoner)
    for key in summoner_eff.keys():
        report_runes["summary"][key] = summoner_eff[key]

    return report_runes


@username_case_redirect
@login_required
def stats_runes(request, profile_name):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'runes': _get_stats_runes(summoner),
        'view': 'stats',
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES},
    }

    return render(request, 'herders/profile/stats/runes/base.html', context)


def _get_stats_rune_crafts(summoner, craft_type):
    if craft_type in RuneCraft.CRAFT_GRINDSTONES:
        stats = {stat[1]: 0 for stat in sorted(
            RuneCraft.STAT_CHOICES, key=lambda x: x[1]) if stat[0] in RuneCraft.STAT_GRINDABLE}
    else:
        stats = {stat[1]: 0 for stat in sorted(
            RuneCraft.STAT_CHOICES, key=lambda x: x[1])}
    sets = {rune_set[1]: 0 for rune_set in sorted(
        RuneCraft.TYPE_CHOICES, key=lambda x: x[1])}
    sets[None] = 0
    qualities = {quality[1]: 0 for quality in RuneCraft.QUALITY_CHOICES}
    report = {
        'sets': copy.deepcopy(sets),
        'quality': copy.deepcopy(qualities),
        'stat': copy.deepcopy(stats),
        'summary': {
            'Count': 0,
            'Worth': 0,
        },
        'detailed': {
            stat: {
                "total": 0,
                "sets": {
                    set_: {"total": 0, "qualities": copy.deepcopy(qualities)}
                    for set_ in sets.keys() if set_ is not None
                }
            }
            for stat in stats.keys()},
    }
    rune_crafts = RuneCraftInstance.objects.select_related(
        'owner').filter(owner=summoner, type=craft_type)

    for record in rune_crafts:
        set_ = record.get_rune_display()
        quality = record.get_quality_display()
        stat = record.get_stat_display()

        report['summary']['Count'] += record.quantity or 0
        report['sets'][set_] += record.quantity or 0
        report['quality'][quality] += record.quantity or 0
        report['stat'][stat] += record.quantity or 0

        if record.value:
            report['summary']['Worth'] += record.value * record.quantity or 0

        if set_:
            report['detailed'][stat]['total'] += record.quantity or 0
            report['detailed'][stat]['sets'][set_]["total"] += record.quantity or 0
            report['detailed'][stat]['sets'][set_]["qualities"][quality] += record.quantity or 0

    return report


@username_case_redirect
@login_required
def stats_rune_crafts(request, profile_name, rune_craft_slug):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    craft_types = {slugify(type_[1]): {"idx": type_[0], "name": type_[
        1]} for type_ in RuneCraft.CRAFT_CHOICES}
    craft_type = craft_types.get(rune_craft_slug, None)
    if craft_type is None:
        return HttpResponseBadRequest()

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'crafts': _get_stats_rune_crafts(summoner, craft_type["idx"]),
        'craft_type': craft_type['name'],
        'immemorial': 'Immemorial' in craft_type['name'],
        'view': 'stats',
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES},
    }

    return render(request, 'herders/profile/stats/runes/crafts.html', context)


def _get_stats_artifacts(summoner):
    qualities = {quality[1]: 0 for quality in Artifact.QUALITY_CHOICES}
    report = {
        'summary': {
            'Count': 0,
        },
        'quality': copy.deepcopy(qualities),
        'quality_original': copy.deepcopy(qualities),
        'slot': {artifact_slot[1]: 0 for artifact_slot in (Artifact.ARCHETYPE_CHOICES + Artifact.NORMAL_ELEMENT_CHOICES)},
        'main_stat': {stat[1]: 0 for stat in sorted(Artifact.MAIN_STAT_CHOICES, key=lambda x: x[1])},
        'substats': {effect[1]: 0 for effect in sorted(Artifact.EFFECT_CHOICES, key=lambda x: x[1])},
    }
    artifacts = ArtifactInstance.objects.select_related(
        'owner').filter(owner=summoner)

    artifact_substats = dict(Artifact.EFFECT_CHOICES)

    report['summary']['Count'] = artifacts.count()
    for artifact in artifacts:
        for sub_stat in artifact.effects:
            report['substats'][artifact_substats[sub_stat]] += 1

        report['quality'][artifact.get_quality_display()] += 1
        report['quality_original'][artifact.get_original_quality_display()] += 1
        report['slot'][artifact.get_precise_slot_display()] += 1
        report['main_stat'][artifact.get_main_stat_display()] += 1

    summoner_eff = _get_efficiency_statistics(ArtifactInstance, summoner)
    for key in summoner_eff.keys():
        report["summary"][key] = summoner_eff[key]

    return report


@username_case_redirect
@login_required
def stats_artifacts(request, profile_name):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'artifacts': _get_stats_artifacts(summoner),
        'view': 'stats',
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES},
    }

    return render(request, 'herders/profile/stats/artifacts/base.html', context)


def _get_stats_artifact_crafts(summoner):
    report = {
        'summary': {
            'Count': 0,
        },
        'quality': {quality[1]: 0 for quality in Artifact.QUALITY_CHOICES},
        'slot': {artifact_slot[1]: 0 for artifact_slot in (Artifact.ARCHETYPE_CHOICES + Artifact.NORMAL_ELEMENT_CHOICES)},
        'substats': {effect[1]: 0 for effect in sorted(Artifact.EFFECT_CHOICES, key=lambda x: x[1])},
    }
    artifacts = ArtifactCraftInstance.objects.select_related(
        'owner').filter(owner=summoner)

    for artifact in artifacts:
        report['substats'][artifact.get_effect_display()] += artifact.quantity or 0
        report['quality'][artifact.get_quality_display()] += artifact.quantity or 0
        report['slot'][artifact.get_archetype_display(
        ) or artifact.get_element_display()] += artifact.quantity or 0
        report['summary']['Count'] += artifact.quantity or 0

    return report


@username_case_redirect
@login_required
def stats_artifact_crafts(request, profile_name):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'artifact_craft': _get_stats_artifact_crafts(summoner),
        'view': 'stats',
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES},
    }

    return render(request, 'herders/profile/stats/artifacts/crafts.html', context)


def _get_stats_monsters(summoner):
    report = {
        'summary': {
            'Count': 0,
            'In Storage': 0,
            'Outside Storage': 0,
            'Max Skillups': 0,
            'Fusion Food': 0,
            'In Monster Shrine Storage': 0,
        },
        'stars': {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        },
        'natural_stars': {
            i: {
                "fusion": {
                    "elemental": 0,
                    "ld": 0,
                },
                "nonfusion": {
                    "elemental": 0,
                    "ld": 0,
                },
            } for i in range(1, 6)},
        'elements': {element[1]: 0 for element in Monster.NORMAL_ELEMENT_CHOICES},
        'archetypes': {archetype[1]: 0 for archetype in Monster.ARCHETYPE_CHOICES},
    }
    monsters = MonsterInstance.objects.select_related('owner', 'monster', 'monster__awakens_to', 'monster__awakens_from',
                                                      'monster__awakens_from__awakens_from', 'monster__awakens_to__awakens_to').prefetch_related('monster__skills').filter(owner=summoner)
    monsters_fusion = [
        f'{mon.product.family_id}-{mon.product.element}' for mon in Fusion.objects.select_related('product').only('product')]
    free_nat5_families = [19200, 23000, 24100, 24600, 1000100, 1000200]

    report['summary']['Count'] = monsters.count()
    for monster in monsters:
        if monster.monster.archetype == Monster.ARCHETYPE_MATERIAL:
            report['summary']['Count'] -= 1
            continue

        if monster.in_storage:
            report['summary']['In Storage'] += 1
        else:
            report['summary']['Outside Storage'] += 1
        if monster.skill_ups_to_max() == 0:
            report['summary']['Max Skillups'] += 1
        report['stars'][monster.stars] += 1

        mon_el = "elemental" if monster.monster.element in [
            Monster.ELEMENT_WATER, Monster.ELEMENT_FIRE, Monster.ELEMENT_WIND] else "ld"
        if f'{monster.monster.family_id}-{monster.monster.element}' in monsters_fusion or monster.monster.family_id in free_nat5_families:
            report['natural_stars'][monster.monster.natural_stars]['fusion'][mon_el] += 1
        else:
            report['natural_stars'][monster.monster.natural_stars]['nonfusion'][mon_el] += 1

        report['elements'][monster.monster.get_element_display()] += 1
        report['archetypes'][monster.monster.get_archetype_display()] += 1

        if monster.monster.fusion_food:
            report['summary']['Fusion Food'] += 1

    monsters_shrine = MonsterShrineStorage.objects.select_related(
        'owner', 'item').filter(owner=summoner)

    for monster in monsters_shrine:
        if monster.item.archetype == Monster.ARCHETYPE_MATERIAL:
            continue

        report['summary']['Count'] += monster.quantity or 0
        report['summary']['In Monster Shrine Storage'] += monster.quantity or 0
        report['stars'][monster.item.natural_stars] += monster.quantity or 0

        mon_el = "elemental" if monster.item.element in [
            Monster.ELEMENT_WATER, Monster.ELEMENT_FIRE, Monster.ELEMENT_WIND] else "ld"
        if f'{monster.item.family_id}-{monster.item.element}' in monsters_fusion or monster.item.family_id in free_nat5_families:
            report['natural_stars'][monster.item.natural_stars]['fusion'][mon_el] += monster.quantity or 0
        else:
            report['natural_stars'][monster.item.natural_stars]['nonfusion'][mon_el] += monster.quantity or 0

        report['elements'][monster.item.get_element_display()
                           ] += monster.quantity or 0
        report['archetypes'][monster.item.get_archetype_display()
                             ] += monster.quantity or 0

    return report


@username_case_redirect
@login_required
def stats_monsters(request, profile_name):
    try:
        summoner = Summoner.objects.select_related(
            'user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return render(request, 'herders/profile/not_public.html', {})

    context = {
        'is_owner': is_owner,
        'profile_name': profile_name,
        'monsters': _get_stats_monsters(summoner),
        'view': 'stats',
        'subviews': {type_[1]: slugify(type_[1]) for type_ in RuneCraft.CRAFT_CHOICES},
    }

    return render(request, 'herders/profile/stats/monsters/base.html', context)


@username_case_redirect
@login_required
def set_consent(request):
    data = request.POST
    c_report = (data['consent-report'] == 'true')
    c_top = (data['consent-top'] == 'true')
    
    summoner = request.user.summoner
    summoner.consent_report = c_report
    summoner.consent_top = c_top
    summoner.save()

    return redirect(request.META.get('HTTP_REFERER'))


@username_case_redirect
@login_required
def recalc_rune_builds(request, profile_name):
    from herders.tasks import update_rune_builds_for_summoner
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponse()

    update_rune_builds_for_summoner.delay(summoner.pk)
    return HttpResponse()
