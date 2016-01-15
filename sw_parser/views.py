from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from herders.models import Summoner, Monster, MonsterInstance, RuneInstance

from .forms import *
from .parser import *


@login_required
def home(request):
    return render(request, 'sw_parser/base.html', context={'view': 'importexport'})


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
                errors += _import_objects(request, data, import_options, summoner)

                if len(errors):
                    messages.warning(request, mark_safe('Import partially successful. See issues below:<br />' + '<br />'.join(errors)))

                return redirect('sw_parser:import_confirm')
    else:
        form = ImportPCAPForm()

    context = {
        'form': form,
        'errors': errors,
        'view': 'import_export'
    }

    return render(request, 'sw_parser/import_pcap.html', context)


@login_required
def import_sw_json(request):
    errors = []

    if request.POST:
        form = ImportSWParserJSONForm(request.POST, request.FILES)

        if form.is_valid():
            summoner = get_object_or_404(Summoner, user__username=request.user.username)
            uploaded_file = form.cleaned_data['json_file']
            import_options = {
                'clear_profile': form.cleaned_data.get('clear_profile'),
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
        'view': 'import_export'
    }

    return render(request, 'sw_parser/import_sw_json.html', context)


@login_required
def export_rune_optimizer(request):
    return render(request, 'sw_parser/coming_soon.html', context={'view': 'importexport'})


@login_required
def import_rune_optimizer(request):
    return render(request, 'sw_parser/coming_soon.html', context={'view': 'importexport'})


@login_required
def commit_import(request):
    summoner = get_object_or_404(Summoner, user__username=request.user.username)

    # List existing com2us IDs and newly imported com2us IDs
    imported_mon_com2us_ids = MonsterInstance.imported.values_list('com2us_id', flat=True).filter(owner=summoner)
    existing_mon_com2us_ids = MonsterInstance.objects.values_list('com2us_id', flat=True).filter(owner=summoner, com2us_id__isnull=False)

    imported_rune_com2us_ids = RuneInstance.imported.values_list('com2us_id', flat=True).filter(owner=summoner)
    existing_rune_com2us_ids = RuneInstance.objects.values_list('com2us_id', flat=True).filter(owner=summoner, com2us_id__isnull=False)

    # Split import into brand new, updated, and existing monsters that were not imported.
    new_mons = MonsterInstance.imported.filter(owner=summoner).exclude(com2us_id__in=existing_mon_com2us_ids)
    updated_mons = MonsterInstance.objects.filter(owner=summoner, com2us_id__in=imported_mon_com2us_ids)
    missing_mons = MonsterInstance.objects.filter(owner=summoner).exclude(com2us_id__in=imported_mon_com2us_ids)

    new_runes = RuneInstance.imported.filter(owner=summoner).exclude(com2us_id__in=existing_rune_com2us_ids)
    updated_runes = RuneInstance.objects.filter(owner=summoner, com2us_id__in=imported_rune_com2us_ids)
    missing_runes = RuneInstance.objects.filter(owner=summoner).exclude(com2us_id__in=imported_rune_com2us_ids)

    context = {
        'monsters': {
            'total_imported': len(imported_mon_com2us_ids),
            'updated': updated_mons,
            'new': new_mons,
            'missing': missing_mons,
        },
        'runes': {
            'total_imported': len(imported_rune_com2us_ids),
            'updated': updated_runes,
            'new': new_runes,
            'missing': missing_runes,
        },
    }

    return render(request, 'sw_parser/import_confirm.html', context)


@login_required
def import_status(request):
    return JsonResponse({
        'stage': request.session.get('import_stage'),
        'total': request.session.get('import_total'),
        'current': request.session.get('import_current'),
    })


def _import_objects(request, data, import_options, summoner):
    errors = []
    # Parsed JSON successfully! Do the import.
    try:
        results = parse_sw_json(data, summoner, import_options)
    except KeyError as e:
        errors.append('Uploaded JSON is missing an expected field: ' + str(e))
    else:
        # Importing objects from JSON didn't fail completely, so let's import what it did
        # Remove all previous import remnants
        MonsterInstance.imported.filter(owner=summoner).delete()
        RuneInstance.imported.filter(owner=summoner).delete()

        errors += results['errors']

        # Update essence storage
        summoner.storage_magic_low = results['inventory'].get('storage_magic_low', 0)
        summoner.storage_magic_mid = results['inventory'].get('storage_magic_mid', 0)
        summoner.storage_magic_high = results['inventory'].get('storage_magic_high', 0)
        summoner.storage_fire_low = results['inventory'].get('storage_fire_low', 0)
        summoner.storage_fire_mid = results['inventory'].get('storage_fire_mid', 0)
        summoner.storage_fire_high = results['inventory'].get('storage_fire_high', 0)
        summoner.storage_water_low = results['inventory'].get('storage_water_low', 0)
        summoner.storage_water_mid = results['inventory'].get('storage_water_mid', 0)
        summoner.storage_water_high = results['inventory'].get('storage_water_high', 0)
        summoner.storage_wind_low = results['inventory'].get('storage_wind_low', 0)
        summoner.storage_wind_mid = results['inventory'].get('storage_wind_mid', 0)
        summoner.storage_wind_high = results['inventory'].get('storage_wind_high', 0)
        summoner.storage_light_low = results['inventory'].get('storage_light_low', 0)
        summoner.storage_light_mid = results['inventory'].get('storage_light_mid', 0)
        summoner.storage_light_high = results['inventory'].get('storage_light_high', 0)
        summoner.storage_dark_low = results['inventory'].get('storage_dark_low', 0)
        summoner.storage_dark_mid = results['inventory'].get('storage_dark_mid', 0)
        summoner.storage_dark_high = results['inventory'].get('storage_dark_high', 0)
        summoner.save()

        # Save the imported monsters
        request.session['import_stage'] = 'monsters'
        request.session['import_total'] = len(results['monsters'])
        request.session['import_current'] = 0
        for idx, mon in enumerate(results['monsters']):
            mon.save()
            if idx % 10 == 0:
                request.session['import_current'] = idx
                request.session.save()

        # Save imported runes
        request.session['import_stage'] = 'runes'
        request.session['import_total'] = len(results['runes'])
        request.session['import_current'] = 0
        for idx, rune in enumerate(results['runes']):
            rune.save()
            if idx % 10 == 0:
                request.session['import_current'] = idx
                request.session.save()

        request.session['import_stage'] = 'done'
    return errors
