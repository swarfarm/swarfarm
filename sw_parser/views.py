from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from bulk_update.helper import bulk_update

from herders.models import Summoner, Monster, MonsterInstance, RuneInstance

from .forms import *
from .parser import *


@login_required
def home(request):
    return render(request, 'sw_parser/home.html')


@login_required
def import_pcap(request):
    return render(request, 'sw_parser/coming_soon.html')


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
                # Parsed JSON successfully! Do the import.
                try:
                    results = parse_sw_json(data, summoner, import_options)
                except KeyError as e:
                    errors.append('Uploaded JSON is missing an expected field: ' + str(e))
                else:
                    if import_options['clear_profile']:
                        MonsterInstance.objects.filter(owner=summoner).delete()
                        RuneInstance.objects.filter(owner=summoner).delete()

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
                    bulk_update(results['monsters']['updated'])
                    MonsterInstance.objects.bulk_create(results['monsters']['new'])

                    # Save imported runes
                    bulk_update(results['runes']['updated'])
                    RuneInstance.objects.bulk_create(results['runes']['new'])

                    # Update monsters with equipped rune stats - can only be done after runes are saved
                    mons_to_update = MonsterInstance.objects.filter(owner=summoner)

                    for mon in mons_to_update:
                        mon.update_fields()

                    bulk_update(mons_to_update)

            return render(request, 'sw_parser/import_successful.html', {'errors': errors})
    else:
        form = ImportSWParserJSONForm()

    context = {
        'form': form,
        'errors': errors,
    }

    return render(request, 'sw_parser/import_sw_json.html', context)


@login_required
def export_rune_optimizer(request):
    return render(request, 'sw_parser/coming_soon.html')


@login_required
def import_rune_optimizer(request):
    return render(request, 'sw_parser/coming_soon.html')
