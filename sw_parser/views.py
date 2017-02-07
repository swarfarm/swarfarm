from collections import OrderedDict
from copy import deepcopy
import csv

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core.mail import mail_admins
from django.core.urlresolvers import reverse
from django.db import IntegrityError, transaction
from django.db.models import Count, Min, Max, Avg, Sum, Value, F, ExpressionWrapper, DurationField
from django.db.models.functions import Coalesce
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.defaultfilters import pluralize
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from bestiary.models import Monster
from herders.models import Summoner, MonsterInstance, RuneInstance, Storage, BuildingInstance

from .forms import *
from .com2us_parser import *
from .com2us_mapping import valid_rune_drop_map
from .log_parser import *
from .rune_optimizer_parser import *
from .db_utils import Percentile
import chart_templates

_named_timestamps = {
    'post-3.2.1': {
        'description': 'Patch 3.2.1 to Present',
        'filters': {
            'timestamp__gte': '2017-01-12T12:30:00+00:00',
        }
    },
    'post-homunculus': {
        'description': 'Patch 3.0.2 to 3.2.1',
        'filters': {
            'timestamp__gte': '2016-09-13T00:00:00+00:00',
            'timestamp__lt': '2017-01-12T12:30:00+00:00',
        }
    },
    'pre-homunculus': {
        'description': 'Beginning to Patch 3.0.2',
        'filters': {
            'timestamp__lte': '2016-09-13'
        }
    },
    'all-time': {
        'description': 'All Time',
        'filters': {
            'timestamp__gte': '2000-01-01',
        }
    },
}

DEFAULT_TIMESTAMP_FILTER = _named_timestamps['post-3.2.1']


@login_required
def home(request):
    return render(request, 'sw_parser/base.html', context={'view': 'importexport'})


@login_required
def import_swarfarm_backup(request):
    return render(request, 'sw_parser/coming_soon.html')


@login_required
def export_swarfarm_backup(request):
    return render(request, 'sw_parser/coming_soon.html')


@transaction.atomic
@login_required
@csrf_exempt
def import_pcap(request):
    request.upload_handlers = [TemporaryFileUploadHandler()]
    return _import_pcap(request)


@csrf_protect
def _import_pcap(request):
    errors = []

    if request.POST:
        form = ImportPCAPForm(request.POST, request.FILES)

        if form.is_valid():
            summoner = get_object_or_404(Summoner, user__username=request.user.username)
            uploaded_file = form.cleaned_data['pcap']
            import_options = {
                'clear_profile': form.cleaned_data.get('clear_profile'),
                'default_priority': form.cleaned_data.get('default_priority'),
                'lock_monsters': form.cleaned_data.get('lock_monsters'),
                'minimum_stars': int(form.cleaned_data.get('minimum_stars', 1)),
                'ignore_silver': form.cleaned_data.get('ignore_silver'),
                'ignore_material': form.cleaned_data.get('ignore_material'),
                'except_with_runes': form.cleaned_data.get('except_with_runes'),
                'except_light_and_dark': form.cleaned_data.get('except_light_and_dark'),
            }

            try:
                data = parse_pcap(uploaded_file)
            except Exception as e:
                errors.append('Exception ' + str(type(e)) + ': ' + str(e))
            else:
                # Import the new objects
                if data:
                    errors += _import_objects(request, data, import_options, summoner)

                    if len(errors):
                        messages.warning(request, mark_safe('Import partially successful. See issues below:<br />' + '<br />'.join(errors)))

                    return redirect('sw_parser:import_confirm')
                else:
                    errors.append("Unable to find Summoner's War data in the capture.")
    else:
        form = ImportPCAPForm()

    context = {
        'form': form,
        'errors': errors,
        'view': 'importexport'
    }

    return render(request, 'sw_parser/import_pcap.html', context)


@transaction.atomic
@login_required
def import_sw_json(request):
    errors = []
    request.session['import_stage'] = None
    request.session['import_total'] = 0
    request.session['import_current'] = 0

    if request.POST:
        request.session['import_stage'] = None
        request.session.save()

        form = ImportSWParserJSONForm(request.POST, request.FILES)

        if form.is_valid():
            summoner = get_object_or_404(Summoner, user__username=request.user.username)
            uploaded_file = form.cleaned_data['json_file']
            import_options = {
                'clear_profile': form.cleaned_data.get('clear_profile'),
                'default_priority': form.cleaned_data.get('default_priority'),
                'lock_monsters': form.cleaned_data.get('lock_monsters'),
                'minimum_stars': int(form.cleaned_data.get('minimum_stars', 1)),
                'ignore_silver': form.cleaned_data.get('ignore_silver'),
                'ignore_material': form.cleaned_data.get('ignore_material'),
                'except_with_runes': form.cleaned_data.get('except_with_runes'),
                'except_light_and_dark': form.cleaned_data.get('except_light_and_dark'),
            }

            try:
                data = json.load(uploaded_file)
            except ValueError as e:
                errors.append('Unable to parse file: ' + str(e))
            except AttributeError:
                errors.append('Issue opening uploaded file. Please try again.')
            else:
                # Import the new objects
                errors += _import_objects(request, data, import_options, summoner)

                if len(errors):
                    messages.warning(request, mark_safe('Import partially successful. See issues below:<br />' + '<br />'.join(errors)))

                return redirect('sw_parser:import_confirm')
    else:
        form = ImportSWParserJSONForm()

    context = {
        'form': form,
        'errors': errors,
        'view': 'importexport',
    }

    return render(request, 'sw_parser/import_sw_json.html', context)


@transaction.atomic
@login_required
def commit_import(request):
    summoner = get_object_or_404(Summoner, user__username=request.user.username)

    # List existing com2us IDs and newly imported com2us IDs
    imported_mon_com2us_ids = MonsterInstance.imported.values_list('com2us_id', flat=True).filter(owner=summoner)
    existing_mon_com2us_ids = MonsterInstance.committed.values_list('com2us_id', flat=True).filter(owner=summoner, com2us_id__isnull=False)

    imported_rune_com2us_ids = RuneInstance.imported.values_list('com2us_id', flat=True).filter(owner=summoner)
    existing_rune_com2us_ids = RuneInstance.committed.values_list('com2us_id', flat=True).filter(owner=summoner, com2us_id__isnull=False)

    # Split import into brand new, updated, and existing monsters that were not imported.
    new_mons = MonsterInstance.imported.filter(owner=summoner).exclude(com2us_id__in=existing_mon_com2us_ids)
    updated_mons = MonsterInstance.imported.filter(owner=summoner, com2us_id__in=existing_mon_com2us_ids)
    missing_mons = MonsterInstance.committed.filter(owner=summoner).exclude(com2us_id__in=imported_mon_com2us_ids)

    context = {
        'view': 'importexport',
        'form': ApplyImportForm(),
    }

    if request.POST:
        form = ApplyImportForm(request.POST or None)
        new_runes = RuneInstance.imported.filter(owner=summoner).exclude(com2us_id__in=existing_rune_com2us_ids)
        updated_runes = RuneInstance.imported.filter(owner=summoner, com2us_id__in=existing_rune_com2us_ids)
        missing_runes = RuneInstance.committed.filter(owner=summoner).exclude(com2us_id__in=imported_rune_com2us_ids)

        if form.is_valid():
            # Delete missing if option was chosen
            if form.cleaned_data['missing_monster_action']:
                missing_mons.delete()

            if form.cleaned_data['missing_rune_action']:
                missing_runes.delete()

            # Delete old runes and set new ones as committed
            RuneInstance.committed.filter(owner=summoner, com2us_id__in=imported_rune_com2us_ids).delete()
            updated_runes.update(uncommitted=False)

            # Update mons - need to copy relations before scrapping the old mons
            for mon in updated_mons:
                # Get the preexisting instance
                old_mon = MonsterInstance.committed.filter(owner=summoner, com2us_id=mon.com2us_id).first()

                # Copy team assignments
                mon.team_leader = old_mon.team_leader.all()
                mon.team_set = old_mon.team_set.all()
                mon.tags = old_mon.tags.all()
                mon.save()

            # Delete the old mons and set new mons as committed
            MonsterInstance.committed.filter(owner=summoner, com2us_id__in=imported_mon_com2us_ids).delete()
            updated_mons.update(uncommitted=False)

            # Add new monsters and runes
            new_mons.update(uncommitted=False)
            new_runes.update(uncommitted=False)

            # Delete old monster pieces and commit new ones
            MonsterPiece.committed.filter(owner=summoner).delete()
            MonsterPiece.imported.filter(owner=summoner).update(uncommitted=False)

            # Delete old rune crafts and commit new ones
            RuneCraftInstance.committed.filter(owner=summoner).delete()
            RuneCraftInstance.imported.filter(owner=summoner).update(uncommitted=False)

            messages.success(request, 'Import successfully applied!')
            return redirect('herders:profile_default', profile_name=summoner.user.username)
    else:
        new_runes = OrderedDict()
        updated_runes = OrderedDict()
        missing_runes = OrderedDict()
        new_rune_count = 0
        updated_rune_count = 0
        missing_rune_count = 0

        for type_idx, type_name in RuneInstance.TYPE_CHOICES:
            new_runes[type_name] = RuneInstance.imported.filter(owner=summoner, type=type_idx).exclude(com2us_id__in=existing_rune_com2us_ids)
            updated_runes[type_name] = RuneInstance.imported.filter(owner=summoner, type=type_idx, com2us_id__in=existing_rune_com2us_ids)
            missing_runes[type_name] = RuneInstance.committed.filter(owner=summoner, type=type_idx).exclude(com2us_id__in=imported_rune_com2us_ids)

            new_rune_count += new_runes[type_name].count()
            updated_rune_count += updated_runes[type_name].count()
            missing_rune_count += missing_runes[type_name].count()

        context['monsters'] = {
            'new': new_mons,
            'updated': updated_mons,
            'missing': missing_mons,
        }
        context['runes'] = {
            'new': new_runes,
            'updated': updated_runes,
            'missing': missing_runes,
        }
        context['new_runes'] = new_rune_count
        context['updated_runes'] = updated_rune_count
        context['missing_runes'] = missing_rune_count

    return render(request, 'sw_parser/import_confirm.html', context)


@login_required()
def import_status(request):
    return render(request, 'sw_parser/import_progress.html')


@login_required
def import_status_data(request):
    return JsonResponse({
        'stage': request.session.get('import_stage'),
        'total': request.session.get('import_total'),
        'current': request.session.get('import_current'),
    })


def _import_objects(request, data, import_options, summoner):
    errors = []
    request.session['import_stage'] = 'parse'
    request.session.save()

    # Parsed JSON successfully! Do the import.
    try:
        results = parse_sw_json(data, summoner, import_options)
    except KeyError as e:
        errors.append('Uploaded data is missing an expected field: ' + str(e))
    except TypeError:
        errors.append('Uploaded data is not valid.')
    else:
        # Everything parsed successfully up to this point, so it's safe to clear the profile now.
        if import_options['clear_profile']:
            RuneInstance.objects.filter(owner=summoner).delete()
            RuneCraftInstance.objects.filter(owner=summoner).delete()
            MonsterInstance.objects.filter(owner=summoner).delete()
            MonsterPiece.objects.filter(owner=summoner).delete()
        else:
            # Delete anything that might have been previously imported
            RuneInstance.imported.filter(owner=summoner).delete()
            RuneCraftInstance.imported.filter(owner=summoner).delete()
            MonsterInstance.imported.filter(owner=summoner).delete()
            MonsterPiece.imported.filter(owner=summoner).delete()

        errors += results['errors']

        # Update summoner and inventory
        if results['wizard_id']:
            summoner.com2us_id = results['wizard_id']
            summoner.save()

        summoner.storage.magic_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_magic_low', 0)
        summoner.storage.magic_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_magic_mid', 0)
        summoner.storage.magic_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_magic_high', 0)
        summoner.storage.fire_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_fire_low', 0)
        summoner.storage.fire_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_fire_mid', 0)
        summoner.storage.fire_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_fire_high', 0)
        summoner.storage.water_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_water_low', 0)
        summoner.storage.water_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_water_mid', 0)
        summoner.storage.water_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_water_high', 0)
        summoner.storage.wind_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_wind_low', 0)
        summoner.storage.wind_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_wind_mid', 0)
        summoner.storage.wind_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_wind_high', 0)
        summoner.storage.light_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_light_low', 0)
        summoner.storage.light_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_light_mid', 0)
        summoner.storage.light_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_light_high', 0)
        summoner.storage.dark_essence[Storage.ESSENCE_LOW] = results['inventory'].get('storage_dark_low', 0)
        summoner.storage.dark_essence[Storage.ESSENCE_MID] = results['inventory'].get('storage_dark_mid', 0)
        summoner.storage.dark_essence[Storage.ESSENCE_HIGH] = results['inventory'].get('storage_dark_high', 0)

        summoner.storage.wood = results['inventory'].get('wood', 0)
        summoner.storage.leather = results['inventory'].get('leather', 0)
        summoner.storage.rock = results['inventory'].get('rock', 0)
        summoner.storage.ore = results['inventory'].get('ore', 0)
        summoner.storage.mithril = results['inventory'].get('mithril', 0)
        summoner.storage.cloth = results['inventory'].get('cloth', 0)
        summoner.storage.rune_piece = results['inventory'].get('rune_piece', 0)
        summoner.storage.dust = results['inventory'].get('powder', 0)
        summoner.storage.symbol_harmony = results['inventory'].get('symbol_harmony', 0)
        summoner.storage.symbol_transcendance = results['inventory'].get('symbol_transcendance', 0)
        summoner.storage.symbol_chaos = results['inventory'].get('symbol_chaos', 0)
        summoner.storage.crystal_water = results['inventory'].get('crystal_water', 0)
        summoner.storage.crystal_fire = results['inventory'].get('crystal_fire', 0)
        summoner.storage.crystal_wind = results['inventory'].get('crystal_wind', 0)
        summoner.storage.crystal_light = results['inventory'].get('crystal_light', 0)
        summoner.storage.crystal_dark = results['inventory'].get('crystal_dark', 0)
        summoner.storage.crystal_magic = results['inventory'].get('crystal_magic', 0)
        summoner.storage.crystal_pure = results['inventory'].get('crystal_pure', 0)
        summoner.storage.save()

        # Save the imported monsters
        request.session['import_stage'] = 'monsters'
        request.session['import_total'] = len(results['monsters'])
        request.session['import_current'] = 0
        for idx, mon in enumerate(results['monsters']):
            mon.save()

            request.session['import_current'] = idx
            request.session.save()

        # Update saved monster pieces
        for piece in results['monster_pieces']:
            piece.save()

        # Save imported runes
        request.session['import_stage'] = 'runes'
        request.session['import_total'] = len(results['runes'])
        request.session['import_current'] = 0
        for idx, rune in enumerate(results['runes']):
            # Refresh the internal assigned_to_id field, as the monster didn't have a PK when the
            # relationship was previously set.
            rune.assigned_to = rune.assigned_to
            try:
                rune.save()
            except IntegrityError:
                errors.append(
                    'Error saving rune with ID ' + str(rune.com2us_id) + ' - assigned to monster that does not exist.')

            request.session['import_current'] = idx
            request.session.save()

        # Save imported rune crafts
        request.session['import_stage'] = 'crafts'
        request.session['import_total'] = len(results['crafts'])
        request.session['import_current'] = 0
        for idx, craft in enumerate(results['crafts']):
            try:
                craft.save()
            except IntegrityError:
                errors.append('Error saving Gem/Grindstone with ID ' + str(craft.com2us_id))

            request.session['import_current'] = idx
            request.session.save()

        request.session['import_stage'] = 'done'
    return errors


@login_required
def import_rune_optimizer(request):
    from django.forms import ValidationError

    summoner = get_object_or_404(Summoner, user=request.user)
    form = ImportOptimizerForm(request.POST or None)
    form.helper.form_action = reverse('sw_parser:import_optimizer')
    import_error = None
    err_rune = None

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data['json_data']

        if 'runes' in data:
            import_count = 0
            valid_runes = []

            # Validate all imported runes
            for rune_data in data['runes']:
                try:
                    rune = import_rune(rune_data)
                    rune.owner = summoner
                    rune.full_clean()
                    import_count += 1
                except ValidationError as e:
                    import_error = e.message_dict
                    err_rune = rune_data.get('id', 'unknown')
                    break
                else:
                    valid_runes.append(rune)
            else:
                # No exceptions! Save the valid runes.
                for rune in valid_runes:
                    rune.save()
                messages.success(request, 'Successfully imported ' + str(import_count) + ' runes.')

                return redirect('herders:runes', profile_name=request.user.username)
        else:
            import_error = 'No runes found in submitted data'

    context = {
        'import_rune_form': form,
        'import_error': import_error,
        'errored_rune': err_rune,
        'view': 'importexport',
    }

    return render(request, 'sw_parser/import_rune_optimizer.html', context)


@login_required
def export_rune_optimizer(request, download_file=False):
    summoner = get_object_or_404(Summoner, user=request.user)

    export_data = export_runes(
        MonsterInstance.committed.filter(owner=summoner),
        RuneInstance.committed.filter(owner=summoner, assigned_to=None),
    )
    if download_file:
        response = HttpResponse(export_data)
        response['Content-Disposition'] = 'attachment; filename=' + request.user.username + '_swarfarm_rune_optimizer_export.json'

        return response
    else:
        form = ExportOptimizerForm(initial={'json_data': export_data})

        return render(request, 'sw_parser/export_rune_optimizer.html', {'export_form': form, 'view': 'importexport'})


@login_required
def export_win10_optimizer(request):
    summoner = get_object_or_404(Summoner, user=request.user)

    export_data = export_win10(summoner)

    response = HttpResponse(export_data)
    response['Content-Disposition'] = 'attachment; filename=' + request.user.username + '_swarfarm_win10_optimizer_export.json'

    return response


def log_home(request):
    date_filter = _get_log_filter_timestamp(request, False)

    context = {
        'stats': _log_stats(request, date_filter=date_filter),
        'timespan': date_filter,
        'view': 'data',
    }

    return render(request, 'sw_parser/log/base.html', context)


@login_required
def log_mine_home(request):
    date_filter =  _get_log_filter_timestamp(request, True)

    context = {
        'mine': True,
        'stats': _log_stats(request, mine=True, date_filter=date_filter),
        'view': 'data',
        'timespan': date_filter,
    }

    return render(request, 'sw_parser/log/base.html', context)


def _log_stats(request, mine=False, date_filter=None):
    if date_filter is None:
        date_filter = _get_log_filter_timestamp(request, mine)

    cache_key = 'general-stats-{}'.format(slugify(date_filter['description']))
    if mine:
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        stats = None
    else:
        summoner = None
        stats = cache.get(cache_key)

    if stats is None:
        total_runs = RunLog.objects.all()
        total_summons = SummonLog.objects.all()

        if mine:
            total_runs = total_runs.filter(summoner=summoner)
            total_summons = total_summons.filter(summoner=summoner)

        stats = OrderedDict()
        stats['total_runs'] = total_runs.count()
        stats['total_summons'] = total_summons.count()
        stats['timespan_runs'] = total_runs.filter(**date_filter['filters']).count()
        stats['timespan_summons'] = total_summons.filter(**date_filter['filters']).count()
        stats['summons'] = OrderedDict()
        stats['dungeons'] = OrderedDict()
        stats['dungeons']['Rune Dungeons'] = OrderedDict()
        stats['dungeons']['Elemental Dungeons'] = OrderedDict()
        stats['dungeons']['Hall of Heroes'] = OrderedDict()
        stats['dungeons']['Other Dungeons'] = OrderedDict()
        stats['rifts'] = OrderedDict()

        # Count summons
        summon_counts = SummonLog.objects.filter(**date_filter['filters'])
        if mine:
            summon_counts = summon_counts.filter(summoner=summoner)

        for cnt in summon_counts.values('summon_method').annotate(count=Count('pk')):
            name = SummonLog.SUMMON_CHOICES[cnt['summon_method']][1]
            stats['summons'][name] = {
                'pk': cnt['summon_method'],
                'slug': SummonLog.SUMMON_CHOICES_DICT[cnt['summon_method']],
                'count': cnt['count'],
            }

        # Count dungeons
        dungeon_counts = RunLog.objects.filter(success=True, **date_filter['filters']).exclude(dungeon__type=Dungeon.TYPE_SCENARIO)
        if mine:
            dungeon_counts = dungeon_counts.filter(summoner=summoner)

        for cnt in dungeon_counts.values('dungeon__name', 'dungeon__type', 'dungeon__slug').annotate(count=Count('pk')).order_by('dungeon__name'):
            if cnt['dungeon__type'] is not None:
                # Only show categorized dungeons in the list
                dungeon_type = Dungeon.TYPE_CHOICES[cnt['dungeon__type']][1]
                stats['dungeons'][dungeon_type][cnt['dungeon__name']] = {
                    'slug': cnt['dungeon__slug'],
                    'count': cnt['count'],
                }

        # Count rifts
        slug_lookup = {v: k for k, v in RiftDungeonLog.RAID_SLUGS.iteritems()}
        rift_counts = RiftDungeonLog.objects.filter(success=True, **date_filter['filters'])
        if mine:
            rift_counts = rift_counts.filter(summoner=summoner)

        for cnt in rift_counts.values('dungeon').annotate(count=Count('pk')).order_by('dungeon'):
            stats['rifts'][RiftDungeonLog.RAID_DICT[cnt['dungeon']]] = {
                'slug': slug_lookup[cnt['dungeon']],
                'count': cnt['count'],
            }

        if not mine:
            cache.set(cache_key, stats, 3600)

    return stats


def log_contribution_chart_data(request, mine=False):
    chart_type = request.GET.get('chart_type')
    days = request.GET.get('days')

    if not days:
        days = 60
    else:
        days = int(days)

    cache_key = 'contribution-chart-{}-{}'.format(chart_type, days)

    if mine:
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        chart = None
    else:
        summoner = None
        chart = cache.get(cache_key)

    if not chart:
        start_date = datetime.datetime.now(pytz.utc) - datetime.timedelta(days=days)

        if chart_type == 'logs_per_day':
            chart = deepcopy(chart_templates.column)
            chart['title']['text'] = 'Logs per Day (last 60 days)'
            chart['plotOptions']['column']['stacking'] = 'normal'
            chart['plotOptions']['column']['groupPadding'] = 0
            chart['plotOptions']['column']['pointPadding'] = 0.05
            chart['plotOptions']['column']['dataLabels'] = {
                'enabled': True,
                'color': 'white',
                'format': '{point.y}',
                'style': {
                    'textShadow': '0 0 3px black'
                }
            }
            chart['xAxis']['labels'] = {'rotation': -90}
            chart['yAxis'] = [
                {'title': {'text': 'Logs'}, 'id': 'logs'},
                {'title': {'text': 'Unique Contributors'}, 'id': 'summoners', 'opposite': True}
            ]
            chart['legend'] = {
                'useHTML': True,
                'align': 'right',
                'x': 0,
                'verticalAlign': 'top',
                'y': 0,
                'floating': True,
                'backgroundColor': 'white',
                'borderColor': '#CCC',
                'borderWidth': 1,
                'shadow': False,
            }

            chart['series'].append({
                'type': 'column',
                'name': 'Dungeon Runs',
                'colorByPoint': False,
                'data': [],
                'yAxis': 'logs',
            })
            chart['series'].append({
                'type': 'column',
                'name': 'Summons',
                'colorByPoint': False,
                'data': [],
                'yAxis': 'logs',
            })
            if not mine:
                chart['series'].append({
                    'type': 'spline',
                    'name': 'Unique Contributors',
                    'colorByPoint': False,
                    'data': [],
                    'yAxis': 'summoners',
                })

            dates = RunLog.objects.filter(timestamp__gte=start_date, timestamp__lt=datetime.datetime.now(pytz.utc)).datetimes('timestamp', 'day', tzinfo=pytz.utc)

            # Query objects on a per-day basis
            for date in dates:
                chart['xAxis']['categories'].append(str(date.date()))
                if mine:
                    runs = RunLog.objects.filter(summoner=summoner, timestamp__gte=date, timestamp__lt=date + datetime.timedelta(days=1))
                    summons = SummonLog.objects.filter(summoner=summoner, timestamp__gte=date, timestamp__lt=date + datetime.timedelta(days=1))
                else:
                    runs = RunLog.objects.filter(timestamp__gte=date, timestamp__lt=date + datetime.timedelta(days=1))
                    summons = SummonLog.objects.filter(timestamp__gte=date, timestamp__lt=date + datetime.timedelta(days=1))

                chart['series'][0]['data'].append(runs.count())
                chart['series'][1]['data'].append(summons.count())

                if not mine:
                    unique_contributors = len(set(list(runs.values_list('wizard_id', flat=True).distinct()) + list(summons.values_list('wizard_id', flat=True).distinct())))
                    chart['series'][2]['data'].append(unique_contributors)

        if not mine:
            cache.set(cache_key, chart, 24*60*60)

    if chart:
        return JsonResponse(chart)


# Summons
def view_summon_log(request, summon_slug, mine=False):
    summon_method = SummonLog.get_summon_method_id(summon_slug)
    date_filter = _get_log_filter_timestamp(request, mine)
    summons = SummonLog.objects.filter(summon_method=summon_method, **date_filter['filters'])
    cache_key = 'summon-log-{}-{}'.format(summon_slug, slugify(date_filter['description']))
    context = None

    if mine:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        summons = summons.filter(summoner=summoner)
    else:
        # Check for a cached version
        context = cache.get(cache_key)

    if context is None:
        grade_range = summons.aggregate(min_grade=Min('monster__grade'), max_grade=Max('monster__grade'))

        context = {
            'stats': _log_stats(request, mine=mine, date_filter=date_filter),
            'timespan': date_filter,
            'summon_method': summon_method,
            'summon_method_name': SummonLog.SUMMON_CHOICES[summon_method][1],
            'count': summons.count(),
            'mine': mine,
            'log_view': 'summon',
        }

        if summons.count():
            context['family_grades'] = range(grade_range['min_grade'], grade_range['max_grade'] + 1)

        if not mine:
            cache.set(cache_key, context, 3600)

    return render(request, 'sw_parser/log/summon_stats.html', context)


def summon_stats_chart_data(request, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)
    summon_method = request.GET.get('summon_method')
    chart_type = request.GET.get('chart_type')
    grade = request.GET.get('grade')
    cache_key = 'summon-chart-{}-{}-{}-{}'.format(summon_method, chart_type, grade, slugify(date_filter['description']))

    if summon_method is None or chart_type is None:
        return HttpResponseBadRequest('Missing chart parameters')

    chart = None
    summons = SummonLog.objects.filter(summon_method=int(summon_method), **date_filter['filters'])

    # Return empty response if nothing to chart
    if not summons.count():
        return JsonResponse(chart_templates.no_data)

    if grade:
        summons = summons.filter(monster__grade=int(grade))

    if mine:
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        summons = summons.filter(summoner=summoner)
    else:
        chart = cache.get(cache_key)

    if chart is None:
        monster_drops = MonsterDrop.objects.filter(summonlog__in=summons)
        chart = _monster_drop_charts(monster_drops, chart_type, grade)

        if chart is None:
            raise Http404()
        elif not mine:
            cache.set(cache_key, chart, 3600)

    return JsonResponse(chart)


# Scenarios
def view_scenario_log_summary(request, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)

    context = None
    cache_key = 'scenario-summary-{}'.format(slugify(date_filter['description']))

    if mine:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse('login'), request.path))
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
    else:
        summoner = None
        context = cache.get(cache_key)

    if context is None:
        # Sortable table of various details about scenarios
        # Mana Dropped (including rune sales)
        # 2* Monster drop rate
        # 3* monster drop rate
        # XP per run
        # XP per energy
        # XP per hour (if mine)
        # maybe craft material drop rates?
        runs = RunLog.objects.filter(dungeon__type=Dungeon.TYPE_SCENARIO, success=True, **date_filter['filters'])

        if mine:
            runs = runs.filter(summoner=summoner)

        # Set up the scenario table
        scenario_stats = OrderedDict()
        for scenario in Dungeon.objects.filter(type=Dungeon.TYPE_SCENARIO).order_by('pk'):
            scenario_stats[scenario.name] = OrderedDict()

            for (difficulty, difficulty_name) in RunLog.DIFFICULTY_CHOICES:
                scenario_stats[scenario.name][difficulty] = []
                for stage in range(scenario.max_floors):
                    energy_cost = scenario.energy_cost[difficulty][stage]
                    xp_gained = scenario.xp[difficulty][stage]

                    scenario_stats[scenario.name][difficulty].append({
                        'scenario_slug': scenario.slug,
                        'runs': None,
                        'difficulty': difficulty_name,
                        'energy_cost': energy_cost,
                        'xp_per_run': xp_gained,
                        'xp_per_energy': None,
                        'xp_per_hour': None,
                        'monster_slots': scenario.monster_slots[difficulty][stage],
                        'mana_per_run': None,
                        'mana_per_energy': None,
                        'mana_per_hour': None,
                        'rune_drop_rate': None,
                        'clear_time': None,
                        'monster_drops': {
                            2: 0,
                            3: 0,
                        },
                        'craft_drops': {
                            ItemDrop.DROP_CRAFT_WOOD: 0,
                            ItemDrop.DROP_CRAFT_LEATHER: 0,
                            ItemDrop.DROP_CRAFT_ROCK: 0,
                            ItemDrop.DROP_CRAFT_ORE: 0,
                            ItemDrop.DROP_CRAFT_MITHRIL: 0,
                            ItemDrop.DROP_CRAFT_CLOTH: 0,
                            ItemDrop.DROP_CRAFT_POWDER: 0,
                        }
                    })

        # Query the various types of stats we care about
        run_stats = runs.values('dungeon__name', 'difficulty', 'stage').annotate(mana=Avg('mana'), count=Count('pk'), clear_time=ExpressionWrapper(Avg('clear_time'), output_field=DurationField()))
        run_energy_drops = runs.filter(energy__isnull=False).values('dungeon__name', 'difficulty', 'stage').annotate(energy=Avg('energy'), count=Count('pk'))
        rune_values = RuneDrop.objects.filter(runlog__in=runs).annotate(dungeon__name=F('runlog__dungeon__name'), difficulty=F('runlog__difficulty'), stage=F('runlog__stage')).values('dungeon__name', 'difficulty', 'stage').annotate(value=Avg('value'), count=Count('pk'))
        monster_drops = runs.filter(drop_monster__isnull=False, drop_monster__grade__gte=2).values('drop_monster__grade', 'drop_monster__level', 'stage', 'difficulty', 'dungeon__name').annotate(count=Count('pk'))
        craft_drops = runs.filter(drop_type__in=ItemDrop.DROP_GENERAL_CRAFTS).values('dungeon__name', 'difficulty', 'stage', 'drop_type').annotate(avg_qty=Avg('drop_quantity'), count=Count('pk'))

        # Fill it in one group of stats at a time
        for energy_drop in run_energy_drops:
            if energy_drop['count'] > 100:
                dungeon = energy_drop['dungeon__name']
                difficulty = energy_drop['difficulty']
                stage = energy_drop['stage'] - 1

                scenario_stats[dungeon][difficulty][stage]['energy_cost'] -= energy_drop['energy']

        for stat in run_stats:
            dungeon = stat['dungeon__name']
            difficulty = stat['difficulty']
            stage = stat['stage'] - 1
            clear_time = stat['clear_time'].total_seconds()

            energy_spent = scenario_stats[dungeon][difficulty][stage]['energy_cost']
            if energy_spent > 0:
                scenario_stats[dungeon][difficulty][stage]['xp_per_energy'] = float(scenario_stats[dungeon][difficulty][stage]['xp_per_run']) / energy_spent

            scenario_stats[dungeon][difficulty][stage]['runs'] = stat['count']
            scenario_stats[dungeon][difficulty][stage]['mana_per_run'] = stat['mana']

            scenario_stats[dungeon][difficulty][stage]['clear_time'] = clear_time

            if mine:
                # Calculate mana and XP per hour
                scenario_stats[dungeon][difficulty][stage]['xp_per_hour'] = scenario_stats[dungeon][difficulty][stage]['xp_per_run'] * (3600.0 / clear_time)
                scenario_stats[dungeon][difficulty][stage]['mana_per_hour'] = stat['mana'] * (3600.0 / clear_time)

        for rune_value in rune_values:
            dungeon = rune_value['dungeon__name']
            difficulty = rune_value['difficulty']
            stage = rune_value['stage'] - 1
            total_runs = scenario_stats[dungeon][difficulty][stage]['runs']

            if total_runs > 0:
                # Add mana from selling runes (rune value * drop rate)
                rune_mana = rune_value['value'] * float(rune_value['count']) / total_runs

                scenario_stats[dungeon][difficulty][stage]['mana_per_run'] += rune_mana

            # Calculate mana per energy now that we have the final mana value
            energy_spent = scenario_stats[dungeon][difficulty][stage]['energy_cost']
            if energy_spent > 0:
                scenario_stats[dungeon][difficulty][stage]['mana_per_energy'] = float(scenario_stats[dungeon][difficulty][stage]['mana_per_run']) / energy_spent

        for monster_drop in monster_drops:
            dungeon = monster_drop['dungeon__name']
            difficulty = monster_drop['difficulty']
            stage = monster_drop['stage'] - 1
            total_runs = scenario_stats[dungeon][difficulty][stage]['runs']

            level = monster_drop['drop_monster__level']
            grade = monster_drop['drop_monster__grade']

            # Count rainbowmon as one star higher.
            if level == 10 + grade * 5:
                grade += 1

            if total_runs > 0:
                drop_chance = float(monster_drop['count']) / total_runs * 100.0
                scenario_stats[dungeon][difficulty][stage]['monster_drops'][grade] += drop_chance

        for craft_drop in craft_drops:
            dungeon = craft_drop['dungeon__name']
            difficulty = craft_drop['difficulty']
            stage = craft_drop['stage'] - 1
            total_runs = scenario_stats[dungeon][difficulty][stage]['runs']

            if total_runs > 0:
                drop_rate = float(craft_drop['count']) / total_runs
                scenario_stats[dungeon][difficulty][stage]['craft_drops'][craft_drop['drop_type']] = drop_rate * craft_drop['avg_qty']

        context = {
            'mine': mine,
            'stats': _log_stats(request, mine=mine, date_filter=date_filter),
            'log_view': 'scenarios',
            'timespan': date_filter,
            'scenario_stats': scenario_stats,
        }

        if not mine:
            cache.set(cache_key, context, 3600)

    return render(request, 'sw_parser/log/scenarios/summary.html', context)


# Dungeons
def view_dungeon_log(request, dungeon_slug, floor=None, difficulty=None, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)

    try:
        dungeon = Dungeon.objects.get(slug=dungeon_slug)
        if not floor:
            if dungeon.type in [Dungeon.TYPE_ESSENCE_DUNGEON, Dungeon.TYPE_RUNE_DUNGEON, Dungeon.TYPE_OTHER_DUNGEON]:
                floor = dungeon.max_floors
            elif dungeon.type == Dungeon.TYPE_SCENARIO:
                # Automatically choose the one with the most logs
                floor = RunLog.objects.filter(dungeon=dungeon).values_list('stage', flat=True).annotate(count=Count('pk')).order_by('-count').first()
            else:
                floor = 1
        else:
            floor = int(floor)

        floor = min(max(floor, 1), dungeon.max_floors)

        if difficulty is None:
            if dungeon.type == Dungeon.TYPE_SCENARIO:
                # Automatically choose hell for scenarios
                difficulty = RunLog.DIFFICULTY_HELL
            else:
                difficulty = RunLog.DIFFICULTY_NORMAL
        else:
            # Ensure it's cast as an integer
            difficulty = int(difficulty)

    except Dungeon.DoesNotExist:
        raise Http404

    context = None
    cache_key = 'dungeon-log-{}-{}-{}-{}'.format(dungeon_slug, floor, difficulty, slugify(date_filter['description']))

    if mine:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse('login'), request.path))
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
    else:
        summoner = None
        context = cache.get(cache_key)

    if context is None:
        success_rate = None
        run_times = None

        if dungeon.type == Dungeon.TYPE_HALL_OF_HEROES:
            context = {
                'dungeon': dungeon,
                'stages': [],
                'mine': mine,
                'stats': _log_stats(request, mine=mine, date_filter=date_filter),
                'log_view': 'Hall of Heroes',
                'timespan': date_filter,
                'total_runs': 0,
            }

            # Determine the monster for the dungeon
            monster = None
            run_with_drop = RunLog.objects.filter(dungeon=dungeon, drop_monster__isnull=False).first()

            if run_with_drop:
                monster = run_with_drop.drop_monster.monster

            context['monster'] = monster

            # Generate stats for each floor
            for x in range(1, dungeon.max_floors + 1):
                runs = RunLog.objects.filter(dungeon=dungeon, stage=x, success=True, **date_filter['filters'])

                if mine:
                    runs = runs.filter(summoner=summoner)
                    total_runs = RunLog.objects.filter(summoner=summoner, dungeon=dungeon, stage=x, success__isnull=False, **date_filter['filters']).count()

                    if total_runs:
                        success_rate = float(runs.count()) / total_runs * 100
                    else:
                        success_rate = None

                    if runs.count():
                        # Calculate the min and average run time. Todo: find a better way to do this maybe.
                        clear_times = runs.values_list('clear_time', flat=True)
                        avg_clear_time = sum(clear_times, datetime.timedelta(0)) / len(clear_times)
                        min_clear_time = datetime.timedelta.max
                        max_clear_time = datetime.timedelta.min

                        for ct in clear_times:
                            if ct < min_clear_time:
                                min_clear_time = ct
                            if ct > max_clear_time:
                                max_clear_time = ct

                        run_times = {
                            'min': min_clear_time,
                            'max': max_clear_time,
                            'avg': avg_clear_time,
                        }

                pieces_stats = runs.aggregate(min_pieces=Min(Coalesce('drop_quantity', Value(0))), max_pieces=Max(Coalesce('drop_quantity', Value(0))), avg_pieces=Avg(Coalesce('drop_quantity', Value(0))))
                pieces_drops = {
                    'min': pieces_stats['min_pieces'],
                    'max': pieces_stats['max_pieces'],
                    'avg': pieces_stats['avg_pieces'],
                }

                context['total_runs'] += runs.count()
                context['stages'].append({
                    'floor': x,
                    'runs': runs.count(),
                    'general_drops': _get_general_drop_stats(runs),
                    'piece_drops': pieces_drops,
                    'success_rate': success_rate,
                    'clear_times': run_times,
                })

            context['template'] = 'sw_parser/log/hall_of_heroes_stats.html'

        else:
            runs = RunLog.objects.filter(dungeon=dungeon, stage=floor, success=True, **date_filter['filters'])

            if dungeon.type == Dungeon.TYPE_SCENARIO:
                runs = runs.filter(difficulty=difficulty)
            else:
                difficulty = 0  # Default value for non-scenarios

            if mine:
                runs = runs.filter(summoner=summoner)

                if dungeon.type == Dungeon.TYPE_SCENARIO:
                    total_runs = RunLog.objects.filter(summoner=summoner, dungeon=dungeon, stage=floor, difficulty=difficulty, success__isnull=False, **date_filter['filters']).count()
                else:
                    total_runs = RunLog.objects.filter(summoner=summoner, dungeon=dungeon, stage=floor, success__isnull=False, **date_filter['filters']).count()

                if total_runs:
                    success_rate = float(runs.count()) / total_runs * 100
                else:
                    success_rate = None

                if runs.count():
                    # Calculate the min and average run time. Todo: find a better way to do this maybe.
                    clear_times = runs.values_list('clear_time', flat=True)
                    avg_clear_time = sum(clear_times, datetime.timedelta(0)) / len(clear_times)
                    min_clear_time = datetime.timedelta.max
                    max_clear_time = datetime.timedelta.min

                    for ct in clear_times:
                        if ct < min_clear_time:
                            min_clear_time = ct
                        if ct > max_clear_time:
                            max_clear_time = ct

                    run_times = {
                        'min': min_clear_time,
                        'max': max_clear_time,
                        'avg': avg_clear_time,
                    }

            item_drops = OrderedDict()
            stats = runs.filter(drop_type__in=RunLog.DROP_ITEMS).values('drop_type').annotate(count=Count('drop_quantity'), sum=Sum('drop_quantity'), min_qty=Min('drop_quantity'), max_qty=Max('drop_quantity'), avg_qty=Avg('drop_quantity')).order_by('-count')
            total_runs = runs.count()

            for item in stats:
                item_drops[item['drop_type']] = {
                    'min': item['min_qty'],
                    'max': item['max_qty'],
                    'avg': item['avg_qty'],
                    'drop_chance': float(item['count']) / total_runs * 100,
                    'avg_per_run': float(item['sum']) / total_runs,
                    'icon': RunLog.DROP_ICONS.get(item['drop_type']),
                    'description': RunLog.get_drop_type_string(item['drop_type']),
                }

            context = {
                'dungeon': dungeon,
                'floor': floor,
                'floors': [],
                'total_runs': runs.count(),
                'general_drops': _get_general_drop_stats(runs),
                'item_drops': item_drops,
                'mine': mine,
                'success_rate': success_rate,
                'clear_times': run_times,
                'stats': _log_stats(request, mine=mine, date_filter=date_filter),
                'timespan': date_filter,
            }

            # Calculate mana efficiency based on energy
            energy_cost = dungeon.energy_cost[difficulty][floor - 1]
            energy_spent = energy_cost - (context['general_drops']['energy']['avg'] or 0)

            if 'rune' in context['general_drops']:
                rune_value = context['general_drops']['rune']['avg']
                rune_drop_rate = float(runs.filter(drop_type=RunLog.DROP_RUNE).count()) / context['total_runs']
            else:
                rune_drop_rate = 0
                rune_value = 0

            if energy_spent != 0:
                context['mana_efficiency'] = ((context['general_drops']['mana']['avg'] or 0) + rune_value * rune_drop_rate) / energy_spent
            else:
                context['mana_efficiency'] = ((context['general_drops']['mana']['avg'] or 0) + rune_value * rune_drop_rate) / energy_cost

            # Generate list of floors and the number of runs each
            for x in range(0, dungeon.max_floors):
                if mine:
                    floor_count = RunLog.objects.filter(summoner=summoner, dungeon=dungeon, stage=x + 1, success=True, **date_filter['filters']).count()
                else:
                    floor_count = RunLog.objects.filter(dungeon=dungeon, stage=x + 1, success=True, **date_filter['filters']).count()

                context['floors'].append((x + 1, floor_count))

            # Monster drops
            context['monster_drops'] = runs.filter(drop_monster__isnull=False)\
                .values('drop_monster__monster__image_filename', 'drop_monster__grade', 'drop_monster__monster__is_awakened', 'drop_monster__monster__can_awaken')\
                .annotate(count=Count('pk'), level=Avg('drop_monster__level')).order_by('drop_monster__monster__can_awaken', 'drop_monster__grade', 'drop_monster__monster__name')

            for data in context['monster_drops']:
                if data['count']:
                    data['drop_chance'] = float(data['count']) / context['total_runs'] * 100

            if dungeon.type == Dungeon.TYPE_RUNE_DUNGEON:
                context['rune_types'] = [RuneDrop.TYPE_CHOICES[type_id - 1] for type_id in valid_rune_drop_map[int(dungeon.pk)]]
                context['log_view'] = 'Rune Dungeons'
                context['template'] = 'sw_parser/log/rune_dungeon_stats.html'

            elif dungeon.type == Dungeon.TYPE_ESSENCE_DUNGEON:
                # Build a essence drop per energy/run table
                context['essence_table'] = []
                essence_data = runs.filter(drop_type__in=RunLog.DROP_ESSENCES).values('drop_type').annotate(drop_qty=Sum('drop_quantity')).order_by('-drop_qty')
                drop_dict = dict(RunLog.DROP_CHOICES)

                for essence in essence_data:
                    context['essence_table'].append({
                        'essence': drop_dict[essence['drop_type']],
                        'icon': RunLog.DROP_ICONS[essence['drop_type']],
                        'per_run': float(essence['drop_qty']) / context['total_runs'],
                        'per_energy': float(essence['drop_qty']) / context['total_runs'] / energy_spent,
                    })

                context['log_view'] = 'Elemental Dungeons'
                context['template'] = 'sw_parser/log/essence_dungeon_stats.html'

            elif dungeon.type == Dungeon.TYPE_SCENARIO:
                context['difficulty'] = RunLog.DIFFICULTY_CHOICES[difficulty]
                context['difficulties'] = []

                for diff, name in RunLog.DIFFICULTY_CHOICES:
                    if mine:
                        run_count = RunLog.objects.filter(summoner=summoner, dungeon=dungeon.pk, stage=floor, difficulty=diff, success=True, **date_filter['filters']).count()
                    else:
                        run_count = RunLog.objects.filter(dungeon=dungeon.pk, stage=floor, difficulty=diff, success=True, **date_filter['filters']).count()

                    context['difficulties'].append({
                        'id': diff,
                        'name': name,
                        'count': run_count
                    })

                context['log_view'] = 'Scenarios'
                context['template'] = 'sw_parser/log/scenarios/detailed_stats.html'

            elif dungeon.type == Dungeon.TYPE_OTHER_DUNGEON:
                context['log_view'] = 'Other Dungeons'

                context['template'] = 'sw_parser/log/generic_dungeon_stats.html'
            else:
                context['template'] = 'sw_parser/log/coming_soon.html'

        if not mine:
            cache.set(cache_key, context, 3600)

    return render(request, context['template'], context)


def _get_general_drop_stats(runs):
    stats = runs.aggregate(
        min_mana=Min(Coalesce('mana', Value(0))), max_mana=Max(Coalesce('mana', Value(0))), avg_mana=Avg(Coalesce('mana', Value(0))),
        min_crystals=Min(Coalesce('crystal', Value(0))), max_crystals=Max(Coalesce('crystal', Value(0))), avg_crystals=Avg(Coalesce('crystal', Value(0))),
    )
    energy_drops = runs.filter(energy__isnull=False).aggregate(min_energy=Min(Coalesce('energy', Value(0))), max_energy=Max(Coalesce('energy', Value(0))), avg_energy=Avg(Coalesce('energy', Value(0))))
    rune_drop_values = RuneDrop.objects.filter(runlog__in=runs).aggregate(avg=Avg('value'), min=Min('value'), max=Max('value'))

    general_drops = OrderedDict()
    general_drops['mana'] = {
        'min': stats['min_mana'],
        'max': stats['max_mana'],
        'avg': stats['avg_mana'],
    }

    general_drops['energy'] = {
        'min': energy_drops['min_energy'],
        'max': energy_drops['max_energy'],
        'avg': energy_drops['avg_energy'],
    }

    general_drops['crystal'] = {
        'min': stats['min_crystals'],
        'max': stats['max_crystals'],
        'avg': stats['avg_crystals'],
    }

    if rune_drop_values['min']:
        general_drops['rune'] = {
            'desc': ' value',
            'min': rune_drop_values['min'],
            'max': rune_drop_values['max'],
            'avg': rune_drop_values['avg'],
        }

    return general_drops


def dungeon_stats_chart_data(request, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)
    dungeon_id = request.GET.get('dungeon_id')
    floor = request.GET.get('floor')
    chart_type = request.GET.get('chart_type')
    difficulty = request.GET.get('difficulty')

    cache_key = 'dungeon-stats-chart-{}-{}-{}-{}-{}'.format(dungeon_id, floor, chart_type, difficulty, slugify(date_filter['description']))

    if dungeon_id is None or floor is None:
        return HttpResponseBadRequest('Missing chart parameters')

    chart = None
    runs = RunLog.objects.filter(dungeon=int(dungeon_id), stage=int(floor), success=True, **date_filter['filters'])

    if mine:
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        runs = runs.filter(summoner=summoner)
    else:
        chart = cache.get(cache_key)

    if chart is None:

        if difficulty is not None:
            runs = runs.filter(difficulty=int(difficulty))

        # Nothing to chart, return empty response.
        if not runs.count():
            return JsonResponse(chart_templates.no_data)

        chart = None

        if chart_type == 'drop_types':
            chart = deepcopy(chart_templates.pie)
            data = runs.filter(drop_type__isnull=False).exclude(drop_type__in=RunLog.DROP_ESSENCES).values('drop_type').annotate(drop_count=Count('drop_type')).values_list('drop_type', 'drop_count').order_by('-drop_count')
            total_essences = runs.filter(drop_type__in=RunLog.DROP_ESSENCES).values('drop_type').aggregate(drop_count=Count('drop_type'))
            drop_dict = dict(RunLog.DROP_CHOICES)

            # Post-process results
            chart['series'].append({
                'name': 'Drop Types',
                'colorByPoint': True,
                'data': [],
            })
            for point in data:
                chart['series'][0]['data'].append({
                    'name': drop_dict[point[0]],
                    'y': point[1],
                })

            # Insert sum of all awakening essences in appropriate place in the list
            for x, point in enumerate(chart['series'][0]['data']):
                if total_essences['drop_count'] >= point['y']:
                    chart['series'][0]['data'].insert(x, {'name': 'Awakening Essence', 'y': total_essences['drop_count']})
                    break

        elif chart_type == 'summoning_pieces':
            chart = deepcopy(chart_templates.pie)
            data = runs.values('drop_quantity').annotate(count=Count('pk'))

            # Post-process results
            chart['series'].append({
                'name': 'Pieces Dropped',
                'colorByPoint': True,
                'data': []
            })

            for point in data:
                if point['drop_quantity']:
                    value = point['drop_quantity']
                else:
                    value = 0

                chart['series'][0]['data'].append({
                    'name': str(value) + ' piece' + pluralize(value),
                    'y': point['count'],
                })

        elif chart_type == 'essences':
            chart = deepcopy(chart_templates.pie)
            chart['plotOptions']['pie']['colors'] = []
            chart['series'].append({
                'name': 'Essences',
                'colorByPoint': True,
                'data': [],
            })

            data = runs.filter(drop_type__in=RunLog.DROP_ESSENCES).values('drop_type').annotate(drop_count=Sum('drop_quantity')).order_by('-drop_count')
            drop_dict = dict(RunLog.DROP_CHOICES)

            # Post process results
            color_map = {
                RunLog.DROP_ESSENCE_MAGIC_LOW: '#aa00aa',
                RunLog.DROP_ESSENCE_MAGIC_MID: '#cc00cc',
                RunLog.DROP_ESSENCE_MAGIC_HIGH: '#ff00ff',
                RunLog.DROP_ESSENCE_FIRE_LOW: '#aa0000',
                RunLog.DROP_ESSENCE_FIRE_MID: '#cc0000',
                RunLog.DROP_ESSENCE_FIRE_HIGH: '#ff0000',
                RunLog.DROP_ESSENCE_WATER_LOW: '#0000aa',
                RunLog.DROP_ESSENCE_WATER_MID: '#0000cc',
                RunLog.DROP_ESSENCE_WATER_HIGH: '#0000ff',
                RunLog.DROP_ESSENCE_WIND_LOW: '#aaaa00',
                RunLog.DROP_ESSENCE_WIND_MID: '#cccc00',
                RunLog.DROP_ESSENCE_WIND_HIGH: '#ffff00',
                RunLog.DROP_ESSENCE_LIGHT_LOW: '#bfbfbf',
                RunLog.DROP_ESSENCE_LIGHT_MID: '#d9d9d9',
                RunLog.DROP_ESSENCE_LIGHT_HIGH: '#f2f2f2',
                RunLog.DROP_ESSENCE_DARK_LOW: '#595959',
                RunLog.DROP_ESSENCE_DARK_MID: '#404040',
                RunLog.DROP_ESSENCE_DARK_HIGH: '#262626',
            }

            for point in data:
                chart['series'][0]['data'].append({
                    'name': drop_dict[point['drop_type']],
                    'y': point['drop_count']
                })
                chart['plotOptions']['pie']['colors'].append(color_map[point['drop_type']])

        if chart is None:
            raise Http404()
        elif not mine:
            cache.set(cache_key, chart, 3600)

    return JsonResponse(chart)


def dungeon_rune_chart_data(request, mine=False):
    date_filter = deepcopy(_get_log_filter_timestamp(request, mine))
    # Convert date filters to reference the run log since we are querying from the RuneDrop model
    for k, v in date_filter['filters'].iteritems():
        del date_filter['filters'][k]
        date_filter['filters']['runlog__{}'.format(k)] = v

    dungeon_id = request.GET.get('dungeon_id')
    floor = request.GET.get('floor')
    rune_type = request.GET.get('rune_type')
    chart_type = request.GET.get('chart_type')
    difficulty = request.GET.get('difficulty')
    slot = request.GET.get('slot')

    if dungeon_id is not None:
        dungeon_id = int(dungeon_id)

    if floor is not None:
        floor = int(floor)

    if difficulty is not None:
        difficulty = int(difficulty)

    if rune_type is not None:
        rune_type = int(rune_type)

    if slot is not None:
        slot = int(slot)

    cache_key = 'dungeon-rune-chart-{}-{}-{}-{}-{}-{}-{}'.format(dungeon_id, floor, chart_type, difficulty, rune_type, slot, slugify(date_filter['description']))
    chart = None
    runes = RuneDrop.objects.filter(runlog__dungeon=dungeon_id, runlog__stage=floor, **date_filter['filters'])

    if mine:
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        runes = runes.filter(runlog__summoner=summoner)
    else:
        chart = cache.get(cache_key)

    if chart is None:
        if rune_type is not None:
            runes = runes.filter(type=rune_type)

        if difficulty is not None:
            runes = runes.filter(runlog__difficulty=difficulty)

        if slot is not None:
            runes = runes.filter(slot=slot)

        chart = _rune_drop_charts(runes, chart_type, slot)

        if chart is None:
            raise Http404()
        elif not mine:
            cache.set(cache_key, chart, 3600)

    return JsonResponse(chart)


# Elemental Rifts
def view_elemental_rift_log(request, rift_slug, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)
    context = None
    cache_key = 'dungeon-log-{}-{}'.format(rift_slug, slugify(date_filter['description']))

    if rift_slug not in RiftDungeonLog.RAID_SLUGS:
        raise Http404()

    if mine:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse('login'), request.path))
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
    else:
        summoner = None
        context = cache.get(cache_key)

    if context is None:
        runs = RiftDungeonLog.objects.filter(**date_filter['filters'])

        if mine:
            runs = runs.filter(summoner=summoner)

        runs = runs.filter(dungeon=RiftDungeonLog.RAID_SLUGS[rift_slug])

        grade_item_table = OrderedDict()

        # Get a list of items and monsters dropped in the rift
        item_list = OrderedDict()
        for item_drop in RiftDungeonItemDrop.objects.filter(log__in=runs).distinct('item').order_by('item'):
            item_list[item_drop.item] = {
                'name': item_drop.get_item_display(),
                'icon': RiftDungeonItemDrop.DROP_ICONS[item_drop.item],
            }

        for monster_drop in RiftDungeonMonsterDrop.objects.all().distinct('monster__name', 'grade').order_by('grade', 'monster__name'):
            item_list[monster_drop.monster.com2us_id] = {
                'name': mark_safe('{}<span class="glyphicon glyphicon-star"></span> {}'.format(monster_drop.grade, monster_drop.monster.name)),
                'icon': 'monsters/' + monster_drop.monster.image_filename,
            }

        # Build the grade table so we include all grades
        for grade in reversed(RiftDungeonLog.GRADE_CHOICES):
            grade_item_table[grade[0]] = {
                'grade': grade[1],
                'total_runs': 0,
                'items': deepcopy(item_list),
            }

        # Add the total runs to each grade
        for grade_counts in runs.values('grade').annotate(count=Count('pk')):
            grade_item_table[grade_counts['grade']]['total_runs'] = grade_counts['count']

        # Calculate avg items dropped per run and chance to drop
        for item_drop in RiftDungeonItemDrop.objects.filter(log__in=runs).values('item', 'log__grade').annotate(
            avg_qty=Avg('quantity'),
            min_qty=Min('quantity'),
            max_qty=Max('quantity'),
            occurences=Count('pk')
        ):
            grade_run_count = grade_item_table[item_drop['log__grade']]['total_runs']
            chance_to_drop = float(item_drop['occurences']) / grade_run_count

            grade_item_table[item_drop['log__grade']]['items'][item_drop['item']]['avg_drop'] = item_drop['avg_qty'] * chance_to_drop
            grade_item_table[item_drop['log__grade']]['items'][item_drop['item']]['avg_qty'] = item_drop['avg_qty']
            grade_item_table[item_drop['log__grade']]['items'][item_drop['item']]['min_qty'] = item_drop['min_qty']
            grade_item_table[item_drop['log__grade']]['items'][item_drop['item']]['max_qty'] = item_drop['max_qty']
            grade_item_table[item_drop['log__grade']]['items'][item_drop['item']]['chance_drop'] = chance_to_drop * 100

        for monster_drop in RiftDungeonMonsterDrop.objects.filter(log__in=runs).values('monster__com2us_id', 'log__grade').annotate(
            occurences=Count('pk'),
        ):
            grade_run_count = grade_item_table[monster_drop['log__grade']]['total_runs']
            chance_to_drop = float(monster_drop['occurences']) / grade_run_count
            grade_item_table[monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['avg_qty'] = 1
            grade_item_table[monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['min_qty'] = 1
            grade_item_table[monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['max_qty'] = 1
            grade_item_table[monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['avg_drop'] = chance_to_drop
            grade_item_table[monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['chance_drop'] = chance_to_drop * 100

        context = {
            'dungeon_name': RiftDungeonLog.RAID_DICT[RiftDungeonLog.RAID_SLUGS[rift_slug]],
            'mine': mine,
            'stats': _log_stats(request, mine=mine, date_filter=date_filter),
            'log_view': 'rift',
            'timespan': date_filter,
            'item_list': item_list,
            'drop_stats': grade_item_table,
        }

    return render(request, 'sw_parser/log/elemental_rift/summary.html', context)


# Rune Crafting
def view_rune_craft_log(request, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)
    context = None
    cache_key = 'rune-craft-log-{}'.format(slugify(date_filter['description']))

    if mine:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse('login'), request.path))
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
    else:
        summoner = None
        context = cache.get(cache_key)

    if context is None:
        craft_logs = RuneCraftLog.objects.filter(craft_level=RuneCraftLog.CRAFT_HIGH, **date_filter['filters'])

        if summoner:
            craft_logs = craft_logs.filter(summoner=summoner)

        context = {
            'stats': _log_stats(request, mine=mine, date_filter=date_filter),
            'timespan': date_filter,
            'count': craft_logs.count(),
            'mine': mine,
            'log_view': 'rune_craft'
        }

        if not mine:
            cache.set(cache_key, context, 3600)

    return render(request, 'sw_parser/log/rune_crafting/summary.html', context)


def rune_craft_chart_data(request, mine=False):
    date_filter = deepcopy(_get_log_filter_timestamp(request, mine))
    # Convert date filters to reference the craft log since we are querying from the RuneDrop model
    for k, v in date_filter['filters'].iteritems():
        del date_filter['filters'][k]
        date_filter['filters']['log__{}'.format(k)] = v

    chart_type = request.GET.get('chart_type')
    slot = request.GET.get('slot')

    if slot:
        slot = int(slot)

    cache_key = 'rune-craft-chart-{}-{}-{}'.format(chart_type, slot, slugify(date_filter['description']))
    chart = None
    runes = RuneCraft.objects.filter(log__craft_level=RuneCraftLog.CRAFT_HIGH, **date_filter['filters'])

    if mine:
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        runes = runes.filter(runlog__summoner=summoner)
    else:
        chart = cache.get(cache_key)

    if chart is None:
        if slot:
            runes = runes.filter(slot=slot)

        chart = _rune_drop_charts(runes, chart_type, slot)

        if chart is None:
            raise Http404()
        elif not mine:
            cache.set(cache_key, chart, 3600)

    return JsonResponse(chart)


# Magic Shop
def view_magic_shop_log(request, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)
    context = None
    cache_key = 'magic-shop-{}'.format(slugify(date_filter['description']))

    if mine:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse('login'), request.path))
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
    else:
        summoner = None
        context = cache.get(cache_key)

    if context is None:
        shop_logs = ShopRefreshLog.objects.filter(**date_filter['filters'])

        if mine:
            shop_logs = shop_logs.filter(summoner=summoner)

        total_logs = shop_logs.count()

        # Item drop table
        item_drops = OrderedDict()

        for item in ShopRefreshItem.objects.filter(log__in=shop_logs).values('item').annotate(
                count=Count('pk'), avg_qty=Avg('quantity'), avg_cost=Avg('cost'),
        ).order_by('-count'):
            appearance_chance = float(item['count']) / total_logs
            refreshes_per_item = 1 / appearance_chance if appearance_chance > 0 else None

            item_drops[item['item']] = {
                'avg_qty': item['avg_qty'],
                'avg_cost': item['avg_cost'],
                'appearance_chance': appearance_chance * 100,
                'avg_cost_per_item': item['avg_qty'] / item['avg_cost'],
                'avg_crystal_per_item': refreshes_per_item * 3 if refreshes_per_item else None,
                'icon': ItemDrop.DROP_ICONS.get(item['item']),
                'description': ItemDrop.DROP_CHOICES_DICT.get(item['item']),
            }

        context = {
            'mine': mine,
            'stats': _log_stats(request, mine=mine, date_filter=date_filter),
            'log_view': 'magic_shop',
            'count': total_logs,
            'item_details': item_drops,
            'timespan': date_filter,
        }

        if total_logs:
            monster_grade_range = ShopRefreshMonster.objects.filter(log__in=shop_logs).aggregate(min_grade=Min('grade'), max_grade=Max('grade'))
            context['grade_range'] = range(monster_grade_range['min_grade'], monster_grade_range['max_grade'] + 1)
        else:
            context['count'] = 'No'

    return render(request, 'sw_parser/log/magic_shop/summary.html', context)


def magic_shop_chart_data(request, mine=False):
    date_filter = deepcopy(_get_log_filter_timestamp(request, mine))
    chart_type = request.GET.get('chart_type')
    section = request.GET.get('section')
    slot = request.GET.get('slot')
    if slot:
        slot = int(slot)

    cache_key = 'magic-shop-chart-{}-{}-{}'.format(chart_type, slot, slugify(date_filter['description']))
    chart = None

    shop_logs = ShopRefreshLog.objects.filter(**date_filter['filters'])

    if mine:
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        shop_logs = shop_logs.filter(owner=summoner)
    else:
        chart = cache.get(cache_key)

    if chart is None:
        if section:
            if section == 'rune':
                runes = ShopRefreshRune.objects.filter(log__in=shop_logs)
                chart = _rune_drop_charts(runes, chart_type, slot)

            elif section == 'monster':
                grade = request.GET.get('grade')
                monsters = ShopRefreshMonster.objects.filter(log__in=shop_logs)

                if grade:
                    monsters = monsters.filter(grade=int(grade))

                chart = _monster_drop_charts(monsters, chart_type, grade)

            elif section == 'scrolls':
                pass
        else:
            if chart_type == 'summary':
                chart = deepcopy(chart_templates.column)
                chart['title']['text'] = 'Frequency of appearance'
                chart['xAxis']['labels'] = {
                    'rotation': -90,
                    'useHTML': True,
                }
                chart['yAxis']['title']['text'] = 'Chance to Appear'
                chart['yAxis']['labels'] = {
                    'format': '{value}%',
                }
                chart['plotOptions']['column']['dataLabels'] = {
                    'enabled': True,
                    'color': 'white',
                    'format': '{point.y:.1f}%',
                    'style': {
                        'textShadow': '0 0 3px black'
                    }
                }
                chart['series'].append({
                    'name': 'Type of Drop',
                    'colorByPoint': True,
                    'data': [],
                })

                total_logs = shop_logs.count()
                appearance_chances = []
                # appearance_chance = float(item['count']) / total_logs

                # Items
                for drop in ShopRefreshItem.objects.filter(log__in=shop_logs).values('item').annotate(count=Count('pk')):
                    appearance_chances.append((
                        float(drop['count']) / total_logs * 100,
                        ShopRefreshItem.DROP_CHOICES_DICT[drop['item']]
                    ))

                # Monsters by grade
                for drop in ShopRefreshMonster.objects.filter(log__in=shop_logs).values('grade').annotate(count=Count('pk')):
                    appearance_chances.append((
                        float(drop['count']) / total_logs * 100,
                        '{}<span class="glyphicon glyphicon-star"></span> Monster'.format(drop['grade'])
                    ))

                # Runes by grade
                for drop in ShopRefreshRune.objects.filter(log__in=shop_logs).values('stars').annotate(count=Count('pk')):
                    appearance_chances.append((
                        float(drop['count']) / total_logs * 100,
                        '{}<span class="glyphicon glyphicon-star"></span> Rune'.format(drop['stars'])
                    ))

                # Sort the list by appearance chance
                appearance_chances.sort(reverse=True)

                # Fill in the chart data and categories
                for point in appearance_chances:
                    chart['xAxis']['categories'].append(point[1])
                    chart['series'][0]['data'].append(point[0])

        if chart is None:
            raise Http404()
        elif not mine:
            cache.set(cache_key, chart, 3600)

    return JsonResponse(chart)


# World Boss
def view_world_boss_log(request, mine=False):
    date_filter = _get_log_filter_timestamp(request, mine)
    context = None
    cache_key = 'world-boss-{}'.format(slugify(date_filter['description']))

    if mine:
        if not request.user.is_authenticated():
            return redirect('%s?next=%s' % (reverse('login'), request.path))
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
    else:
        summoner = None
        context = cache.get(cache_key)

    if context is None:
        boss_logs = WorldBossLog.objects.filter(**date_filter['filters'])

        if mine:
            boss_logs = boss_logs.filter(summoner=summoner)

        grade_item_table = OrderedDict()

        # Get a list of items and monsters dropped in the rift.
        # Split into separate lists by category of: Summoning Items, Essences/Currency, Monsters, Runes
        summoning_item_list = OrderedDict()
        essence_item_list = OrderedDict()
        monster_list = OrderedDict()

        # Summoning items
        for item_drop in WorldBossItemDrop.objects.filter(item__in=WorldBossItemDrop.DROP_SUMMONING).distinct('item').order_by('item'):
            summoning_item_list[item_drop.item] = {
                'name': item_drop.get_item_display(),
                'icon': WorldBossItemDrop.DROP_ICONS[item_drop.item],
            }
        # Essences/currency
        item_drop_list = WorldBossItemDrop.DROP_ESSENCES + WorldBossItemDrop.DROP_CURRENCY
        for item_drop in WorldBossItemDrop.objects.filter(item__in=item_drop_list).distinct('item').order_by('item'):
            essence_item_list[item_drop.item] = {
                'name': item_drop.get_item_display(),
                'icon': WorldBossItemDrop.DROP_ICONS[item_drop.item],
            }

        # Monsters
        for monster_drop in WorldBossMonsterDrop.objects.all().distinct('monster__name', 'monster__element').order_by('monster__name', 'monster__element'):
            monster_list[monster_drop.monster.com2us_id] = {
                'name': mark_safe('{}<span class="glyphicon glyphicon-star"></span> {}'.format(monster_drop.grade, monster_drop.monster.name)),
                'icon': 'monsters/' + monster_drop.monster.image_filename,
            }

        essence_item_list['rune'] = {
            'name': 'Rune',
            'icon': 'icons/rune.png',
        }

        # Build the grade table so we include all grades
        grade_item_table['summoning'] = OrderedDict()
        grade_item_table['items'] = OrderedDict()
        grade_item_table['monsters'] = OrderedDict()

        for grade in reversed(RiftDungeonLog.GRADE_CHOICES):
            grade_item_table['summoning'][grade[0]] = {
                'grade': grade[1],
                'total_runs': 0,
                'items': deepcopy(summoning_item_list),
            }
            grade_item_table['items'][grade[0]] = {
                'grade': grade[1],
                'total_runs': 0,
                'items': deepcopy(essence_item_list),
            }
            grade_item_table['monsters'][grade[0]] = {
                'grade': grade[1],
                'total_runs': 0,
                'items': deepcopy(monster_list),
            }

        # Add the total runs to each grade
        for grade_counts in boss_logs.values('grade').annotate(count=Count('pk')):
            grade_item_table['summoning'][grade_counts['grade']]['total_runs'] = grade_counts['count']
            grade_item_table['items'][grade_counts['grade']]['total_runs'] = grade_counts['count']
            grade_item_table['monsters'][grade_counts['grade']]['total_runs'] = grade_counts['count']

        # Calculate avg items dropped per run and chance to drop
        for item_drop in WorldBossItemDrop.objects.filter(log__in=boss_logs).values('item', 'log__grade').annotate(
            avg_qty=Avg('quantity'),
            min_qty=Min('quantity'),
            max_qty=Max('quantity'),
            occurences=Count('pk')
        ):
            if item_drop['item'] in WorldBossItemDrop.DROP_SUMMONING:
                item_type = 'summoning'
            elif item_drop['item'] in item_drop_list:
                item_type = 'items'
            else:
                continue

            grade_run_count = grade_item_table[item_type][item_drop['log__grade']]['total_runs']
            chance_to_drop = float(item_drop['occurences']) / grade_run_count

            grade_item_table[item_type][item_drop['log__grade']]['items'][item_drop['item']]['avg_drop'] = item_drop['avg_qty'] * chance_to_drop
            grade_item_table[item_type][item_drop['log__grade']]['items'][item_drop['item']]['avg_qty'] = item_drop['avg_qty']
            grade_item_table[item_type][item_drop['log__grade']]['items'][item_drop['item']]['min_qty'] = item_drop['min_qty']
            grade_item_table[item_type][item_drop['log__grade']]['items'][item_drop['item']]['max_qty'] = item_drop['max_qty']
            grade_item_table[item_type][item_drop['log__grade']]['items'][item_drop['item']]['chance_drop'] = chance_to_drop * 100

        for monster_drop in WorldBossMonsterDrop.objects.filter(log__in=boss_logs).values('monster__com2us_id', 'log__grade').annotate(
            occurences=Count('pk'),
        ):
            grade_run_count = grade_item_table['monsters'][monster_drop['log__grade']]['total_runs']
            chance_to_drop = float(monster_drop['occurences']) / grade_run_count
            grade_item_table['monsters'][monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['avg_qty'] = 1
            grade_item_table['monsters'][monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['min_qty'] = 1
            grade_item_table['monsters'][monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['max_qty'] = 1
            grade_item_table['monsters'][monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['avg_drop'] = chance_to_drop
            grade_item_table['monsters'][monster_drop['log__grade']]['items'][monster_drop['monster__com2us_id']]['chance_drop'] = chance_to_drop * 100

        for rune_drop in WorldBossRuneDrop.objects.filter(log__in=boss_logs).values('log__grade').annotate(
            occurences=Count('pk')
        ):
            grade_run_count = grade_item_table['items'][rune_drop['log__grade']]['total_runs']
            chance_to_drop = float(rune_drop['occurences']) / grade_run_count

            grade_item_table['items'][rune_drop['log__grade']]['items']['rune']['avg_qty'] = 1
            grade_item_table['items'][rune_drop['log__grade']]['items']['rune']['min_qty'] = 1
            grade_item_table['items'][rune_drop['log__grade']]['items']['rune']['max_qty'] = 1
            grade_item_table['items'][rune_drop['log__grade']]['items']['rune']['avg_drop'] = chance_to_drop
            grade_item_table['items'][rune_drop['log__grade']]['items']['rune']['chance_drop'] = chance_to_drop * 100

        context = {
            'dungeon_name': "Primal Giant Pan'ghor",
            'mine': mine,
            'stats': _log_stats(request, mine=mine, date_filter=date_filter),
            'log_view': 'world_boss',
            'timespan': date_filter,
            'item_lists': {
                'Summoning Scrolls': {
                    'item_list': summoning_item_list,
                    'stats': grade_item_table['summoning'],
                },
                'Items and Currency': {
                    'item_list': essence_item_list,
                    'stats': grade_item_table['items'],
                },
                'Monsters': {
                    'item_list': monster_list,
                    'stats': grade_item_table['monsters'],
                },
            },
        }

    return render(request, 'sw_parser/log/world_boss/summary.html', context)


# Utility functions to provide some common data across multiple log reports
def _rune_drop_charts(runes, chart_type, slot=None):
    # Produces various charts from a queryset from any model subclassing RuneDrop.
    chart = None

    if slot:
        runes = runes.filter(slot=slot)

    total_runes = runes.count()

    # Return empty response if nothing to chart
    if not total_runes:
        return deepcopy(chart_templates.no_data)

    if chart_type == 'star_summary':
        chart = deepcopy(chart_templates.pie)
        chart['title']['text'] = 'Drops Rate By Stars'
        data = runes.values('stars').annotate(count=Count('pk')).order_by('stars')

        # Post-process results
        chart['series'].append({
            'name': 'Slot',
            'colorByPoint': True,
            'data': [],
            'dataLabels': {
                'distance': 5,
            },
        })

        for point in data:
            chart['series'][0]['data'].append({
                'name': str(point['stars']) + '<span class="glyphicon glyphicon-star"></span>',
                'y': point['count'],
            })

    elif chart_type == 'star_detail':
        # Multi-series bar chart by grade
            chart = deepcopy(chart_templates.column)
            chart['title']['text'] = 'Stars Breakdown By Rune'
            chart['plotOptions']['column']['stacking'] = 'normal'
            chart['plotOptions']['column']['groupPadding'] = 0
            chart['plotOptions']['column']['pointPadding'] = 0.05
            chart['plotOptions']['column']['dataLabels'] = {
                'enabled': True,
                'color': 'white',
                'format': '{point.y:.1f}%',
                'style': {
                    'textShadow': '0 0 3px black'
                }
            }
            chart['yAxis']['title']['text'] = 'Percentage'
            chart['yAxis']['stackLabels'] = {
                'enabled': True,
                'format': '{total:.1f}%',
                'style': {
                    'fontWeight': 'bold',
                    'color': 'gray',
                }
            }

            chart['legend'] = {
                'useHTML': True,
                'align': 'right',
                'x': 0,
                'verticalAlign': 'top',
                'y': 25,
                'floating': True,
                'backgroundColor': 'white',
                'borderColor': '#CCC',
                'borderWidth': 1,
                'shadow': False,
            }

            runes_types_in_set = runes.values_list('type', flat=True).order_by('type').distinct()
            rune_types = [RuneDrop.TYPE_CHOICES[type_id - 1] for type_id in runes_types_in_set]
            grade_range = runes.values('stars').aggregate(min=Min('stars'), max=Max('stars'))

            data = {rune_type[0]: {
                grade: 0 for grade in range(grade_range['min'], grade_range['max'] + 1)
            } for rune_type in rune_types}

            # Post-process data
            for result in runes.values('stars', 'type').annotate(count=Count('pk')).order_by('type', 'stars'):
                data[result['type']][result['stars']] = result['count']

            # Build the chart series
            categories = [rune_type[1] for rune_type in rune_types]
            series = []

            for grade in range(grade_range['min'], grade_range['max'] + 1):
                values = []
                for rune_type in rune_types:
                    values.append(float(data[rune_type[0]][grade]) / total_runes * 100)

                series.append({
                    'name': str(grade) + '<span class="glyphicon glyphicon-star"></span>',
                    'data': values,
                })

            chart['series'] = series
            chart['xAxis']['categories'] = categories

    elif chart_type == 'quality_summary':
        chart = deepcopy(chart_templates.pie)
        chart['title']['text'] = 'Drops Rate By Quality'
        data = runes.values('quality').annotate(count=Count('pk')).order_by('quality')

        rune_quality_dict = dict(RuneDrop.QUALITY_CHOICES)

        # Post-process results
        chart['series'].append({
            'name': 'Slot',
            'colorByPoint': True,
            'data': [],
            'colors': [],
            'dataLabels': {
                'distance': 5,
            },
        })

        for point in data:
            chart['series'][0]['data'].append({
                'name': rune_quality_dict[point['quality']],
                'y': point['count'],
            })
            chart['series'][0]['colors'].append(RuneDrop.QUALITY_COLORS[point['quality']])

    elif chart_type == 'quality_detail':
        # Multi-series bar chart by grade
        chart = deepcopy(chart_templates.column)
        chart['title']['text'] = 'Drop Rate By Quality'
        chart['subtitle'] = {
            'text': 'Each grade normalized to 100%'
        }
        chart['plotOptions']['column']['stacking'] = 'normal'
        chart['plotOptions']['column']['groupPadding'] = 0
        chart['plotOptions']['column']['pointPadding'] = 0.05
        chart['plotOptions']['column']['dataLabels'] = {
            'enabled': True,
            'color': 'white',
            'format': '{point.y:.1f}%',
            'style': {
                'textShadow': '0 0 3px black'
            }
        }
        chart['yAxis']['title']['text'] = 'Percentage'
        chart['yAxis']['stackLabels'] = {
            'enabled': True,
            'format': '{total:.1f}%',
            'style': {
                'fontWeight': 'bold',
                'color': 'gray',
            }
        }

        chart['legend'] = {
            'useHTML': True,
            'align': 'right',
            'x': 0,
            'verticalAlign': 'top',
            'y': 25,
            'floating': True,
            'backgroundColor': 'white',
            'borderColor': '#CCC',
            'borderWidth': 1,
            'shadow': False,
        }

        star_range = runes.values('stars').aggregate(min=Min('stars'), max=Max('stars'))
        rune_stars = range(star_range['min'], star_range['max']+1)
        star_counts = {result['stars']: result['count'] for result in runes.values('stars').annotate(count=Count('pk'))}
        quality_range = runes.values('quality').aggregate(min=Min('quality'), max=Max('quality'))

        data = {rune_star: {
            quality[0]: 0 for quality in RuneDrop.QUALITY_CHOICES
        } for rune_star in rune_stars}

        # Post-process data
        for result in runes.values('quality', 'stars').annotate(count=Count('pk')).order_by('stars', 'quality'):
            data[result['stars']][result['quality']] = result['count']

        # Build the chart series
        categories = ['{}<span class="glyphicon glyphicon-star"></span>'.format(rune_star) for rune_star in rune_stars]
        series = []

        for x in range(quality_range['min'], quality_range['max'] + 1):
            quality = RuneDrop.QUALITY_CHOICES[x]
            values = []
            for rune_star in rune_stars:
                values.append(float(data[rune_star][quality[0]]) / star_counts[rune_star] * 100)

            series.append({
                'name': quality[1],
                'data': values,
                'color': RuneDrop.QUALITY_COLORS[x],
            })

        chart['series'] = series
        chart['xAxis']['categories'] = categories

    elif chart_type == 'main_stat_summary':
        # Pareto of substat occurence frequency
        chart = deepcopy(chart_templates.column)
        chart['title']['text'] = 'Main Stat Frequency - Slot {}'.format(slot)
        chart['xAxis']['labels'] = {'rotation': -90}
        chart['yAxis']['title']['text'] = 'Chance of Appearing'
        chart['plotOptions']['column']['dataLabels'] = {
            'enabled': True,
            'color': 'gray',
            'format': '{point.y:.1f}%',
            'style': {
                'textShadow': '0 0 3px white'
            }
        }
        chart['series'].append({
            'name': 'Family',
            'colorByPoint': False,
            'data': [],
        })
        chart['series'][0]['name'] = 'Family'

        stat_counts = {
            RuneDrop.STAT_HP: 0,
            RuneDrop.STAT_HP_PCT: 0,
            RuneDrop.STAT_ATK: 0,
            RuneDrop.STAT_ATK_PCT: 0,
            RuneDrop.STAT_DEF: 0,
            RuneDrop.STAT_DEF_PCT: 0,
            RuneDrop.STAT_SPD: 0,
            RuneDrop.STAT_CRIT_RATE_PCT: 0,
            RuneDrop.STAT_CRIT_DMG_PCT: 0,
            RuneDrop.STAT_RESIST_PCT: 0,
            RuneDrop.STAT_ACCURACY_PCT: 0,
        }

        for data in runes.values('main_stat').annotate(count=Count('pk')).order_by('-count'):
            stat_counts[data['main_stat']] += data['count']

        for stat in sorted(stat_counts, key=stat_counts.get, reverse=True):
            chart['xAxis']['categories'].append(RuneDrop.STAT_CHOICES[stat-1][1])
            chart['series'][0]['data'].append(stat_counts[stat] / float(total_runes) * 100)

    elif chart_type == 'innate_stat_summary':
        # Pareto of substat occurence frequency
        chart = deepcopy(chart_templates.column)
        chart['title']['text'] = 'Innate Stat Frequency'
        chart['subtitle'] = {
            'text': 'Percentage chance for an innate stat to appear on a rune of any quality'
        }
        chart['xAxis']['labels'] = {'rotation': -90}
        chart['yAxis']['title']['text'] = 'Chance of Appearing'
        chart['plotOptions']['column']['dataLabels'] = {
            'enabled': True,
            'color': 'gray',
            'format': '{point.y:.1f}%',
            'style': {
                'textShadow': '0 0 3px white'
            }
        }
        chart['series'].append({
            'name': 'Family',
            'colorByPoint': False,
            'data': [],
        })
        chart['series'][0]['name'] = 'Family'

        stat_counts = {
            None: 0,
            RuneDrop.STAT_HP: 0,
            RuneDrop.STAT_HP_PCT: 0,
            RuneDrop.STAT_ATK: 0,
            RuneDrop.STAT_ATK_PCT: 0,
            RuneDrop.STAT_DEF: 0,
            RuneDrop.STAT_DEF_PCT: 0,
            RuneDrop.STAT_SPD: 0,
            RuneDrop.STAT_CRIT_RATE_PCT: 0,
            RuneDrop.STAT_CRIT_DMG_PCT: 0,
            RuneDrop.STAT_RESIST_PCT: 0,
            RuneDrop.STAT_ACCURACY_PCT: 0,
        }

        for data in runes.values('innate_stat').annotate(count=Count('pk')).order_by('-count'):
            stat_counts[data['innate_stat']] += data['count']

        for stat in sorted(stat_counts, key=stat_counts.get, reverse=True):
            if stat is None:
                chart['xAxis']['categories'].append('None')
            else:
                chart['xAxis']['categories'].append(RuneDrop.STAT_CHOICES[stat-1][1])
            chart['series'][0]['data'].append(stat_counts[stat] / float(total_runes) * 100)

    elif chart_type == 'substat_summary':
        # Pareto of substat occurence frequency
        chart = deepcopy(chart_templates.column)
        chart['title']['text'] = 'Substat Frequency'
        chart['subtitle'] = {
            'text': 'Percentage chance for a stat to appear on a rune of any quality'
        }
        chart['xAxis']['labels'] = {'rotation': -90}
        chart['yAxis']['title']['text'] = 'Chance of Appearing'
        chart['plotOptions']['column']['dataLabels'] = {
            'enabled': True,
            'color': 'gray',
            'format': '{point.y:.1f}%',
            'style': {
                'textShadow': '0 0 3px white'
            }
        }
        chart['series'].append({
            'name': 'Family',
            'colorByPoint': False,
            'data': [],
        })
        chart['series'][0]['name'] = 'Family'

        stat_counts = {
            RuneDrop.STAT_HP: 0,
            RuneDrop.STAT_HP_PCT: 0,
            RuneDrop.STAT_ATK: 0,
            RuneDrop.STAT_ATK_PCT: 0,
            RuneDrop.STAT_DEF: 0,
            RuneDrop.STAT_DEF_PCT: 0,
            RuneDrop.STAT_SPD: 0,
            RuneDrop.STAT_CRIT_RATE_PCT: 0,
            RuneDrop.STAT_CRIT_DMG_PCT: 0,
            RuneDrop.STAT_RESIST_PCT: 0,
            RuneDrop.STAT_ACCURACY_PCT: 0,
        }

        for data in runes.filter(substat_1__isnull=False).values('substat_1').annotate(count=Count('substat_1')).order_by('-count'):
            stat_counts[data['substat_1']] += data['count']

        for data in runes.filter(substat_2__isnull=False).values('substat_2').annotate(count=Count('substat_2')).order_by('-count'):
            stat_counts[data['substat_2']] += data['count']

        for data in runes.filter(substat_3__isnull=False).values('substat_3').annotate(count=Count('substat_3')).order_by('-count'):
            stat_counts[data['substat_3']] += data['count']

        for data in runes.filter(substat_4__isnull=False).values('substat_4').annotate(count=Count('substat_4')).order_by('-count'):
            stat_counts[data['substat_4']] += data['count']

        total_substat_count = 0
        for stat, count in stat_counts.iteritems():
            total_substat_count += count

        for stat in sorted(stat_counts, key=stat_counts.get, reverse=True):
            chart['xAxis']['categories'].append(RuneDrop.STAT_CHOICES[stat-1][1])
            chart['series'][0]['data'].append(stat_counts[stat] / float(total_substat_count) * 100)

    elif chart_type == 'by_slot':
            chart = deepcopy(chart_templates.pie)
            chart['title']['text'] = 'Drops Rate By Slot'
            data = runes.values('slot').annotate(count=Count('pk')).order_by('slot')

            # Post-process results
            chart['series'].append({
                'name': 'Slot',
                'colorByPoint': True,
                'data': [],
                'dataLabels': {
                    'distance': 5,
                },
            })

            for point in data:
                chart['series'][0]['data'].append({
                    'name': str(point['slot']),
                    'y': point['count'],
                })

    # elif chart_type == 'efficiency_distribution':
    #     # Scatter plot of efficiency by rune quality
    #     chart = deepcopy(chart_templates.boxplot)
    #     chart['title']['text'] = 'Efficiency By Quality'
    #     chart['series'] = [
    #         {
    #             'name': 'Normal',
    #             'color': RuneDrop.QUALITY_COLORS[RuneDrop.QUALITY_NORMAL],
    #             'data': [],
    #         },
    #         {
    #             'name': 'Magic',
    #             'color': RuneDrop.QUALITY_COLORS[RuneDrop.QUALITY_MAGIC],
    #             'data': [],
    #         },
    #         {
    #             'name': 'Rare',
    #             'color': RuneDrop.QUALITY_COLORS[RuneDrop.QUALITY_RARE],
    #             'data': [],
    #         },
    #         {
    #             'name': 'Hero',
    #             'color': RuneDrop.QUALITY_COLORS[RuneDrop.QUALITY_HERO],
    #             'data': [],
    #         },
    #         {
    #             'name': 'Legend',
    #             'color': RuneDrop.QUALITY_COLORS[RuneDrop.QUALITY_LEGEND],
    #             'data': [],
    #         }
    #     ]
    #
    #     chart_data = {}

    return chart


def _monster_drop_charts(monster_drops, chart_type, grade=None):
    # Produces various charts from a queryset from any model subclassing MonsterDrop.
    chart = None

    if monster_drops.count():
        if chart_type == 'family':
            chart = deepcopy(chart_templates.column)
            chart['title']['text'] = str(grade) + '<span class="glyphicon glyphicon-star"></span> Monsters'
            chart['xAxis']['labels'] = {'rotation': -90}
            chart['yAxis']['title']['text'] = 'Number Summoned'
            chart['series'].append({
                'name': 'Family',
                'colorByPoint': True,
                'data': [],
            })
            chart['series'][0]['name'] = 'Family'

            data = monster_drops.filter(monster__is_awakened=False).values('monster__family_id').annotate(num_monsters=Count('pk')).values_list('num_monsters', 'monster__name').order_by('-num_monsters')[:20]

            for point in data:
                chart['xAxis']['categories'].append(point[1])
                chart['series'][0]['data'].append(point[0])

        elif chart_type == 'grade':
            chart = deepcopy(chart_templates.pie)
            chart['title']['text'] = 'By Grade'

            data = monster_drops.filter(monster__is_awakened=False).values_list('grade').annotate(num_monsters=Count('pk')).order_by('grade')

            # Post-process results
            chart['series'].append({
                'name': 'Grade',
                'colorByPoint': True,
                'data': [],
            })

            for point in data:
                chart['series'][0]['data'].append({
                    'name': str(point[0]) + mark_safe('<span class="glyphicon glyphicon-star"></span>'),
                    'y': point[1],
                })

        elif chart_type == 'element':
            chart = deepcopy(chart_templates.pie)
            chart['title']['text'] = 'By Element'
            data = monster_drops.values_list('monster__element').annotate(num_monsters=Count('monster')).order_by('monster__element')

            # Post-process results
            color_map = {
                Monster.ELEMENT_FIRE: '#D90000',
                Monster.ELEMENT_WATER: '#0012E2',
                Monster.ELEMENT_WIND: '#E1E500',
                Monster.ELEMENT_LIGHT: '#DDDDDD',
                Monster.ELEMENT_DARK: '#333333',
            }
            chart['plotOptions']['pie']['colors'] = []
            chart['series'].append({
                'name': 'Element',
                'colorByPoint': True,
                'data': [],
            })
            for point in data:
                chart['series'][0]['data'].append({
                    'name': str(point[0]).capitalize(),
                    'y': point[1],
                })

                chart['plotOptions']['pie']['colors'].append(color_map[point[0]])

        elif chart_type == 'awakened':
            chart = deepcopy(chart_templates.pie)
            chart['title']['text'] = 'Awakened or Unawakened'
            data = monster_drops.values_list('monster__is_awakened').annotate(num_monsters=Count('monster'))

            # Post-process results
            chart['series'].append({
                'name': 'Awakened',
                'colorByPoint': True,
                'data': [],
            })
            for point in data:
                if point[0]:
                    name = 'Awakened'
                else:
                    name = 'Unawakened'

                chart['series'][0]['data'].append({
                    'name': name,
                    'y': point[1],
                })
    else:
        chart = deepcopy(chart_templates.no_data)

    return chart


@login_required
def download_runs(request):
    summoner = get_object_or_404(Summoner, user__username=request.user.username)
    runs = RunLog.objects.filter(summoner=summoner).select_related('drop_rune', 'drop_monster', 'drop_monster__monster').order_by('-timestamp')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + request.user.username + '_runs.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Timestamp',
        'Server',
        'Dungeon',
        'Stage',
        'Difficulty',
        'Success',
        'Clear Time',
        'Energy',
        'Mana',
        'Crystals',
        'Chest Contents',
        'Quantity',
        'Monster',
        'Monster Element',
        'Monster Stars',
        'Monster Level',
        'Rune',
        'Rune Slot',
        'Rune Stars',
        'Rune Main Stat',
        'Rune Innate Stat',
        'Rune Substat 1',
        'Rune Substat 2',
        'Rune Substat 3',
        'Rune Substat 4',
        'Rune Max Efficiency',
        'Rune Value',
    ])

    for r in runs:
        writer.writerow([
            r.timestamp,
            r.server,
            r.dungeon.name,
            r.stage,
            r.difficulty if r.difficulty else '',
            r.success,
            r.clear_time,
            r.energy if r.energy else '',
            r.mana,
            r.crystal,
            r.get_drop_type_display(),
            r.drop_quantity,
            r.drop_monster.monster.name if r.drop_monster else '',
            r.drop_monster.monster.get_element_display() if r.drop_monster else '',
            r.drop_monster.grade if r.drop_monster else '',
            r.drop_monster.level if r.drop_monster else '',
            r.drop_rune.get_type_display() if r.drop_rune else '',
            r.drop_rune.slot if r.drop_rune else '',
            r.drop_rune.stars if r.drop_rune else '',
            r.drop_rune.get_main_stat_display() + ' +' + str(r.drop_rune.main_stat_value) if r.drop_rune else '',
            r.drop_rune.get_innate_stat_display() + ' +' + str(r.drop_rune.innate_stat_value) if r.drop_rune and r.drop_rune.innate_stat else '',
            r.drop_rune.get_substat_1_display() + ' +' + str(r.drop_rune.substat_1_value) if r.drop_rune and r.drop_rune.substat_1 else '',
            r.drop_rune.get_substat_2_display() + ' +' + str(r.drop_rune.substat_2_value) if r.drop_rune and r.drop_rune.substat_2 else '',
            r.drop_rune.get_substat_3_display() + ' +' + str(r.drop_rune.substat_3_value) if r.drop_rune and r.drop_rune.substat_3 else '',
            r.drop_rune.get_substat_4_display() + ' +' + str(r.drop_rune.substat_4_value) if r.drop_rune and r.drop_rune.substat_4 else '',
            r.drop_rune.max_efficiency if r.drop_rune else '',
            r.drop_rune.value if r.drop_rune else '',
        ])

    return response


@login_required
def download_summons(request):
    summoner = get_object_or_404(Summoner, user__username=request.user.username)
    summons = SummonLog.objects.filter(summoner=summoner).select_related('monster', 'monster__monster')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + request.user.username + '_summons.csv"'
    writer = csv.writer(response)
    writer.writerow(['Timestamp', 'Server', 'Summon Method', 'Monster', 'Element', 'Grade', 'Awakened'])

    for s in summons:
        writer.writerow([
            s.timestamp,
            s.get_server_display(),
            s.get_summon_method_display(),
            s.monster.monster.name,
            s.monster.monster.get_element_display(),
            s.monster.grade,
            s.monster.monster.is_awakened,
        ])

    return response


def log_timespan(request, days=None, name=None):
    success = False
    if request.method == 'POST':
        # Process form with custom timestamps
        form = FilterLogTimeRangeForm(request.POST or None)
        if form.is_valid():
            request.session['data_log_date_filter'] = {
                'description': 'Custom',
                'filters': {
                    'timestamp__gte': form.cleaned_data['start_time'].isoformat(),
                    'timestamp__lte': form.cleaned_data['end_time'].isoformat(),
                },
                'custom_start_time': form.cleaned_data['start_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'custom_end_time': form.cleaned_data['end_time'].strftime('%Y-%m-%d %H:%M:%S'),
            }
            success = True
        else:
            messages.error(request, 'Unable to set specified time range.')

    elif name in _named_timestamps:
        request.session['data_log_date_filter'] = _named_timestamps[name]
        success = True

    elif days:
        try:
            days = int(days)
        except:
            success = False
        else:
            if days in [7, 15, 30]:
                request.session['data_log_date_filter'] = {
                    'description': 'Last {} Days'.format(days),
                    'filters': {
                        'timestamp__gte': (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=pytz.timezone('GMT')) - datetime.timedelta(days=days)).isoformat(),
                    }
                }
                success = True

    else:
        success = False

    return JsonResponse({'success': success})


def _get_log_filter_timestamp(request, mine):
    # Basically just don't allow custom filter in global logs
    date_filter = request.session.get('data_log_date_filter', DEFAULT_TIMESTAMP_FILTER)
    if not mine and date_filter['description'] == 'Custom':
        return DEFAULT_TIMESTAMP_FILTER

    return date_filter


@csrf_exempt
def log_data(request):
    if request.POST:
        result_json = json.loads(request.POST.get('data'))
        if 'command' in result_json:
            # Parse using old methods
            result_type = result_json.get('command')
            try:
                if result_type in ['BattleDungeonResult', 'BattleScenarioResult']:
                    raise Exception('Your SwarfarmLogger pluggin is out of date and nothing is being logged. See https://goo.gl/yF7o7s for details.')
                elif result_type == 'SummonUnit':
                    raise Exception('Your SwarfarmLogger pluggin is out of date and nothing is being logged. See https://goo.gl/yF7o7s for details.')
            except Exception as e:
                return HttpResponseBadRequest(e.message)
            else:
                return HttpResponse('')

        elif 'request' in result_json or 'response' in result_json:
            # New plugin, parse with new methods
            api_command = result_json['request'].get('command')

            if api_command and api_command in log_parse_dispatcher:
                try:
                    log_parse_dispatcher[api_command](result_json)
                except Exception as e:
                    mail_admins(
                        subject='Log Error with {}'.format(api_command),
                        message="""
                        {}
                        --------------
                        {}
                        --------------
                        Error message: {}
                        """.format(api_command, result_json, e.message),
                        fail_silently=True,
                    )
                    return HttpResponseBadRequest(e.message)
                else:
                    return HttpResponse('Log OK')
    else:
        return HttpResponseForbidden()


def log_accepted_commands(request):
    return JsonResponse(accepted_api_params)
