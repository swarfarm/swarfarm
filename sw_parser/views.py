from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadhandler import TemporaryFileUploadHandler
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
                errors += import_objects(data, import_options, summoner)

                if len(errors):
                    messages.warning(request, mark_safe('Import partially successful. See issues below:<br />' + '<br />'.join(errors)))
                else:
                    messages.success(request, 'Import successful!')

                return redirect('herders:profile_default', profile_name=summoner.user.username)
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
                import_objects(data, import_options, summoner)

                if len(errors):
                    messages.warning(request, mark_safe('Import partially successful. See issues below:<br />' + '<br />'.join(errors)))
                else:
                    messages.success(request, 'Import successful!')

                return redirect('herders:profile_default', profile_name=summoner.user.username)
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
