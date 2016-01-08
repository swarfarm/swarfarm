import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from herders.models import Summoner, Monster, MonsterInstance, RuneInstance

from .forms import *
from .parser import *


@login_required
def home(request):
    return render(request, 'sw_parser/home.html')


@login_required
def import_pcap(request):
    pass


@login_required
def import_sw_json(request):
    form = ImportSWParserJSONForm(request.POST, request.FILES)
    errors = []

    if request.method == 'POST' and form.is_valid():
        summoner = get_object_or_404(Summoner, user__username=request.user.username)
        uploaded_file = form.cleaned_data['json_file']
        import_options = {
            'clear_profile': form.cleaned_data.get('clear_profile'),
            'minimum_stars': int(form.cleaned_data.get('minimum_stars', 1)),
            'ignore_silver': form.cleaned_data.get('ignore_silver'),
            'ignore_material': form.cleaned_data.get('ignore_material'),
            'except_with_runes': form.cleaned_data.get('except_with_runes'),
        }

        try:
            data = json.load(uploaded_file)
        except ValueError as e:
            errors.append('Unable to parse file: ' + str(e))
        except AttributeError as e:
            errors.append('Issue opening uploaded file. Please try again.')
        else:
            # Parsed JSON successfully. Check that it has
            if import_options['clear_profile']:
                MonsterInstance.objects.filter(owner=summoner).delete()
                RuneInstance.objects.filter(owner=summoner).delete()
            try:
                errors += parse_sw_json(data, summoner, import_options)
            except KeyError as e:
                errors.append('Uploaded JSON is missing an expected field: ' + str(e))

            return render(request, 'sw_parser/import_successful.html', {'errors': errors})

    context = {
        'form': form,
        'errors': errors,
    }

    return render(request, 'sw_parser/import_sw_json.html', context)


@login_required
def export_rune_optimizer(request):
    pass


@login_required
def import_rune_optimizer(request):
    pass
