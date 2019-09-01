from functools import reduce

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, F, Count, Sum, Value, CharField, Case, When
from django.db.models.functions import Concat
from django.http import Http404, HttpResponseForbidden, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import FormView, ListView, TemplateView

from bestiary.models import Dungeon, Level
from data_log.reports.generate import get_drop_querysets, level_drop_report
from data_log.util import transform_to_dict, slice_records, replace_value_with_choice
from herders.decorators import username_case_redirect
from herders.forms import FilterLogTimestamp, FilterDungeonLogForm, FilterSummonLogForm
from herders.models import Summoner, Monster, RuneInstance
from .base import SummonerMixin, OwnerRequiredMixin


class SectionMixin:
    def get_context_data(self, **kwargs):
        kwargs['view'] = 'data_log'
        kwargs['view_name'] = self.request.resolver_match.view_name

        return super().get_context_data(**kwargs)


# Data log views
class Dashboard(SectionMixin, SummonerMixin, OwnerRequiredMixin, TemplateView):
    template_name = 'herders/profile/data_logs/dashboard.html'

    def get_context_data(self, **kwargs):
        log_counts = {
            'magic_shop': self.summoner.shoprefreshlog_set.count(),
            'wish': self.summoner.wishlog_set.count(),
            'rune_crafting': self.summoner.craftrunelog_set.count(),
            'magic_box': self.summoner.magicboxcraft_set.count(),
            'summons': self.summoner.summonlog_set.count(),
            'dungeons': self.summoner.dungeonlog_set.count(),
            'rift_beast': self.summoner.riftdungeonlog_set.count(),
            'rift_raid': self.summoner.riftraidlog_set.count(),
            'world_boss': self.summoner.worldbosslog_set.count(),
        }
        kwargs['counts'] = log_counts
        kwargs['total'] = reduce(lambda a, b: a + b, log_counts.values())

        return super().get_context_data(**kwargs)


class Help(SectionMixin, SummonerMixin, OwnerRequiredMixin, TemplateView):
    template_name = 'herders/profile/data_logs/help.html'


class BaseDataLogView(SummonerMixin, OwnerRequiredMixin, FormView):
    log_type = None
    timestamp_session_key = 'data_log_timestamps'
    max_records = 2000

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            # Update/apply filters from session storage
            self.form_valid(form)

        return super().get(request, *args, **kwargs)

    def get_initial(self):
        return {
            **self.get_filters(),
            **self.get_timestamp_filters(),
        }

    def form_valid(self, form):
        self.save_filters(form)
        self.save_timestamp_filters(form)

        return super().form_valid(form)

    def get_success_url(self):
        # Back to where it was POSTed from
        return self.request.path

    def get_queryset(self):
        qs = getattr(self.summoner, f'{self.get_log_type()}_set').all()
        query = Q()
        for key, value in {
            **self.get_filters(),
            **self.get_timestamp_filters()
        }.items():
            if value:
                query.add(Q(**{key: value}), Q.AND)

        return qs.filter(query)

    def get_context_data(self, **kwargs):
        kwargs['total_count'] = self.get_queryset().count()
        return super().get_context_data(**kwargs)

    def get_log_type(self):
        if self.log_type is None:
            raise ImproperlyConfigured("log_type is required")
        return self.log_type

    def get_session_key(self):
        return f'data_log_{self.get_log_type()}_filters'

    def save_filters(self, form):
        self.request.session[self.get_session_key()] = {}
        for key, value in form.data.lists():
            if key in form.base_fields and value[0]:
                self.request.session[self.get_session_key()][key] = value

    def get_filters(self):
        return self.request.session.get(self.get_session_key(), {})

    def save_timestamp_filters(self, form):
        # Set timestamps in a separate session key so they span all data log sections
        if self.timestamp_session_key not in self.request.session:
            self.request.session[self.timestamp_session_key] = {}

        timestamp__gte = form.data.get('timestamp__gte')
        if timestamp__gte is not None:
            self.request.session[self.timestamp_session_key]['timestamp__gte'] = timestamp__gte
            self.request.session.modified = True

        timestamp__lte = form.data.get('timestamp__lte')
        if timestamp__lte is not None:
            self.request.session[self.timestamp_session_key]['timestamp__lte'] = timestamp__lte
            self.request.session.modified = True

    def get_timestamp_filters(self):
        return self.request.session.get(self.timestamp_session_key, {})


class TableDataLogView(BaseDataLogView, ListView):
    form_class = FilterLogTimestamp
    paginate_by = 50
    context_object_name = 'logs'


# Dungeons
@username_case_redirect
@login_required
def data_log_dungeon_dashboard(request, profile_name):
    # Dashboard of recent dungeon runs and results
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return HttpResponseForbidden()

    form = FilterDungeonLogForm(request.POST or _get_data_log_filters(request, 'dungeonlog_set'))
    qs = summoner.dungeonlog_set.filter(success__isnull=False)  # Do not include incomplete logs

    if form.is_valid():
        # Apply filter values
        for key, value in form.cleaned_data.items():
            if value:
                qs = qs.filter(**{key: value})

        if request.POST:
            # Save time filter timestamps on POST
            _set_data_log_filters(request, 'dungeonlog_set', form)

    # Limit to 2000 results
    qs = slice_records(qs, maximum_count=MAX_DATA_LOG_RECORDS)
    num_logs = qs.count()

    all_drops = get_drop_querysets(qs)
    recent_drops = {
        'items': all_drops['items'].values(
            'item',
            name=F('item__name'),
            icon=F('item__icon'),
        ).annotate(
            count=Sum('quantity')
        ).order_by('-count') if 'items' in all_drops else [],
        'monsters': replace_value_with_choice(
            list(all_drops['monsters'].values(
                name=F('monster__name'),
                icon=F('monster__image_filename'),
                element=F('monster__element'),
                stars=F('grade'),
                is_awakened=F('monster__is_awakened'),
                can_awaken=F('monster__can_awaken'),
            ).annotate(
                count=Count('pk')
            ).order_by('-count')),
            {'element': Monster.ELEMENT_CHOICES}) if 'monsters' in all_drops else [],
        # 'monster_pieces': 'insert_data_here' if 'monster_pieces' in all_drops else [],
        'runes': replace_value_with_choice(
            list(all_drops['runes'].values(
                'type',
                'quality',
                'stars',
            ).annotate(
                count=Count('pk')
            ).order_by('-count') if 'runes' in all_drops else []),
            {
                'type': RuneInstance.TYPE_CHOICES,
                'quality': RuneInstance.QUALITY_CHOICES,
            }
        ),
        # 'secret_dungeons': 'insert_data_here' if 'runes' in all_drops else [],
    }

    success_rate = float(qs.filter(success=True).count()) / num_logs * 100 if num_logs > 0 else None

    dashboard_data = {
        'energy_spent': {
            'type': 'occurrences',
            'total': num_logs,
            'data': transform_to_dict(
                list(
                    qs.values(
                        'level'
                    ).annotate(
                        dungeon_name=Concat(
                            F('level__dungeon__name'),
                            Value(' B'),
                            F('level__floor'),
                            output_field=CharField()
                        ),
                        count=Sum('level__energy_cost'),
                    ).order_by('-count')
                ),
                name_key='dungeon_name',
            ),
        },
        'recent_drops': recent_drops,
    }

    level_order = qs.values('level').annotate(
        energy_spent=Sum('level__energy_cost')
    ).order_by('-energy_spent').values_list('level', flat=True)
    preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(level_order)])
    level_list = Level.objects.filter(
        pk__in=set(qs.values_list('level', flat=True))
    ).order_by(preserved_order).prefetch_related('dungeon')[:20]

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'view': 'data_log',
        'form': form,
        'total_count': num_logs,
        'records_limited': num_logs == MAX_DATA_LOG_RECORDS,
        'success_rate': success_rate,
        'level_list': level_list,
        'dashboard': dashboard_data,
    }

    return render(request, 'herders/profile/data_logs/dungeons/summary.html', context)


@username_case_redirect
@login_required
def data_log_dungeon_detail(request, profile_name, slug, difficulty=None, floor=None):
    try:
        summoner = Summoner.objects.select_related('user').get(user__username=profile_name)
    except Summoner.DoesNotExist:
        return HttpResponseBadRequest()

    is_owner = (request.user.is_authenticated and summoner.user == request.user)

    if not is_owner:
        return HttpResponseForbidden()

    dung = get_object_or_404(Dungeon.objects.all().prefetch_related('level_set'), slug=slug)
    lvl = None
    levels = dung.level_set.all()

    if difficulty:
        difficulty_id = {v.lower(): k for k, v in dict(Level.DIFFICULTY_CHOICES).items()}.get(difficulty)

        if difficulty_id is None:
            raise Http404()

        levels = levels.filter(difficulty=difficulty_id)

    if floor:
        levels = levels.filter(floor=floor)
    else:
        # Pick first hell level for scenarios, otherwise always last level
        if dung.category == Dungeon.CATEGORY_SCENARIO:
            lvl = levels.filter(difficulty=Level.DIFFICULTY_HELL).first()
            return redirect('herders:data_log_dungeon_detail_difficulty', profile_name=profile_name, slug=dung.slug, difficulty='hell', floor=lvl.floor)
        else:
            lvl = levels.last()

            # Redirect to URL with floor if dungeon has more than 1 floor
            if dung.level_set.count() > 1:
                return redirect('herders:data_log_dungeon_detail', profile_name=profile_name, slug=dung.slug, floor=1)

    if not lvl:
        # Default to first level for all others
        lvl = levels.first()

    if not lvl:
        raise Http404()

    form = FilterLogTimestamp(request.POST or _get_data_log_filters(request, 'dungeonlog_set'))
    qs = summoner.dungeonlog_set.filter(level=lvl)

    if form.is_valid():
        # Apply filter values
        for key, value in form.cleaned_data.items():
            if value:
                qs = qs.filter(**{key: value})

        if request.POST:
            # Save time filter timestamps on POST
            _set_data_log_filters(request, 'dungeonlog_set', form)

    # Limit to 2000 results
    qs = slice_records(qs, maximum_count=MAX_DATA_LOG_RECORDS)
    num_logs = qs.count()
    success_rate = float(qs.filter(success=True).count()) / num_logs * 100 if num_logs else None
    report = level_drop_report(qs)
    start_date = qs.last().timestamp if num_logs else None
    end_date = qs.first().timestamp if num_logs else None

    context = {
        'profile_name': profile_name,
        'summoner': summoner,
        'is_owner': is_owner,
        'view': 'data_log',
        'level': lvl,
        'report': report,
        'form': form,
        'total_count': num_logs,
        'start_date': start_date,
        'end_date': end_date,
        'records_limited': num_logs == MAX_DATA_LOG_RECORDS,
        'success_rate': success_rate,
    }

    return render(request, 'herders/profile/data_logs/dungeons/detail.html', context)


class DungeonLogTable(TableDataLogView):
    log_type = 'dungeonlog'
    form_class = FilterDungeonLogForm
    template_name = 'herders/profile/data_logs/dungeons/table.html'


class ElementalRiftBeastTable(TableDataLogView):
    log_type = 'riftdungeonlog'
    template_name = 'herders/profile/data_logs/rift_beast.html'


class RiftRaidTable(TableDataLogView):
    log_type = 'riftraidlog'
    template_name = 'herders/profile/data_logs/rift_raid.html'


class WorldBossTable(TableDataLogView):
    log_type = 'worldbosslog'
    template_name = 'herders/profile/data_logs/world_boss.html'


class SummonsTable(TableDataLogView):
    log_type = 'summonlog'
    form_class = FilterSummonLogForm
    template_name = 'herders/profile/data_logs/summons.html'


class MagicShopTable(TableDataLogView):
    log_type = 'shoprefreshlog'
    template_name = 'herders/profile/data_logs/magic_shop.html'


class WishesTable(TableDataLogView):
    log_type = 'wishlog'
    template_name = 'herders/profile/data_logs/wish.html'


class RuneCraftingTable(TableDataLogView):
    log_type = 'craftrunelog'
    template_name = 'herders/profile/data_logs/rune_crafting.html'


class MagicBoxCraftingTable(TableDataLogView):
    log_type = 'magicboxcraft'
    template_name = 'herders/profile/data_logs/magic_box.html'


