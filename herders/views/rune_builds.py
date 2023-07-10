from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse

from herders.decorators import username_case_redirect
from herders.filters import RuneBuildFilter
from herders.forms import FilterRuneBuildForm
from herders.models import Summoner, RuneBuild


@username_case_redirect
def runebuilds(request, profile_name):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return render(request, 'herders/profile/not_found.html')

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    filter_form = FilterRuneBuildForm(auto_id="filter_id_%s")
    filter_form.helper.form_action = reverse('herders:rune_builds_inventory', kwargs={'profile_name': profile_name})

    context = {
        'view': 'rune_builds',
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'rune_builds_filter_form': filter_form,
    }

    if is_owner or summoner.public:
        return render(request, 'herders/profile/rune_builds/base.html', context)
    else:
        return render(request, 'herders/profile/not_public.html', context)


@username_case_redirect
def rune_builds_inventory(request, profile_name, view_mode=None, box_grouping=None):
    # If we passed in view mode or sort method, set the session variable and redirect back to base profile URL
    if view_mode:
        request.session['rune_builds_inventory_view_mode'] = view_mode.lower()

    if request.session.modified:
        return HttpResponse("Rune builds view mode cookie set")
    view_mode = request.session.get('rune_builds_inventory_view_mode', 'list').lower()

    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)
    
    rune_builds_queryset = RuneBuild.objects.filter(owner=summoner)\
        .prefetch_related('runes', 'artifacts')\
        .select_related('monster')
    total_count = rune_builds_queryset.count()
    form = FilterRuneBuildForm(request.GET or None)

    if form.is_valid():
        rune_builds_filter = RuneBuildFilter(form.cleaned_data, queryset=rune_builds_queryset, summoner=summoner)
    else:
        rune_builds_filter = RuneBuildFilter(None, queryset=rune_builds_queryset, summoner=summoner)

    filtered_count = rune_builds_filter.qs.count()

    context = {
        'rune_builds': rune_builds_filter.qs,
        'total_count': total_count,
        'filtered_count': filtered_count,
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
    }

    if is_owner or summoner.public:
        if view_mode == 'grid':
            template = 'herders/profile/rune_builds/inventory_grid.html'
        else:
            template = 'herders/profile/rune_builds/inventory_table.html'

        return render(request, template, context)
    else:
        return render(request, 'herders/profile/not_public.html', context)
