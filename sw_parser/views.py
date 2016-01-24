from collections import OrderedDict

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
                'default_priority': form.cleaned_data.get('default_priority'),
                'ignore_fusion': form.cleaned_data.get('ignore_fusion'),
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
                'default_priority': form.cleaned_data.get('default_priority'),
                'ignore_fusion': form.cleaned_data.get('ignore_fusion'),
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
    existing_mon_com2us_ids = MonsterInstance.committed.values_list('com2us_id', flat=True).filter(owner=summoner, com2us_id__isnull=False)

    imported_rune_com2us_ids = RuneInstance.imported.values_list('com2us_id', flat=True).filter(owner=summoner)
    existing_rune_com2us_ids = RuneInstance.committed.values_list('com2us_id', flat=True).filter(owner=summoner, com2us_id__isnull=False)

    # Split import into brand new, updated, and existing monsters that were not imported.
    new_mons = MonsterInstance.imported.filter(owner=summoner).exclude(com2us_id__in=existing_mon_com2us_ids)
    updated_mons = MonsterInstance.imported.filter(owner=summoner, com2us_id__in=existing_mon_com2us_ids)
    missing_mons = MonsterInstance.committed.filter(owner=summoner).exclude(com2us_id__in=imported_mon_com2us_ids)

    context = {
        'view': 'import_export',
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
        errors.append('Uploaded data is missing an expected field: ' + str(e))
    except TypeError:
        errors.append('Uploaded data is not valid.')
    else:
        # Everything parsed successfully up to this point, so it's safe to clear the profile now.
        if import_options['clear_profile']:
            RuneInstance.objects.filter(owner=summoner).delete()
            MonsterInstance.objects.filter(owner=summoner).delete()

        # Delete anything that might have been previously imported
        RuneInstance.imported.filter(owner=summoner).delete()
        MonsterInstance.imported.filter(owner=summoner).delete()
        MonsterPiece.imported.filter(owner=summoner).delete()

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

        # Update saved monster pieces
        for piece in results['monster_pieces']:
            piece.save()

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
            # Refresh the internal assigned_to_id field, as the monster didn't have a PK when the
            # relationship was previously set.
            rune.assigned_to = rune.assigned_to
            rune.save()
            if idx % 10 == 0:
                request.session['import_current'] = idx
                request.session.save()

        request.session['import_stage'] = 'done'
    return errors
