from functools import reduce

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Q, F, Count, Sum, Value, CharField, Case, When
from django.db.models.functions import Concat
from django.http import Http404
from django.views.generic import FormView, ListView, TemplateView

from bestiary.models import Dungeon, Level
from data_log.reports.generate import get_drop_querysets, level_drop_report
from data_log.util import transform_to_dict, replace_value_with_choice
from herders.forms import FilterLogTimestamp, FilterDungeonLogForm, FilterSummonLogForm
from herders.models import Monster, RuneInstance
from .base import SummonerMixin, OwnerRequiredMixin


class SectionMixin:
    def get_context_data(self, **kwargs):
        kwargs['view'] = 'data_log'
        kwargs['view_name'] = self.request.resolver_match.view_name

        return super().get_context_data(**kwargs)


# Generic views
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


class DataLogView(SectionMixin, SummonerMixin, OwnerRequiredMixin, FormView):
    log_type = None
    form_class = FilterLogTimestamp
    timestamp_session_key = 'data_log_timestamps'
    log_count = None
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

        qs = qs.filter(query)

        # Trim queryset to max number of records, if defined
        num_records = qs.count()
        if self.max_records and num_records > self.max_records:
            temp_slice = qs[:self.max_records]
            earliest_record = temp_slice[temp_slice.count() - 1]
            qs = qs.filter(timestamp__gte=earliest_record.timestamp)

        return qs

    def get_context_data(self, **kwargs):
        context = {
            'total_count': self.get_log_count(),
            'records_limited': self.max_records and self.get_log_count() == self.max_records
        }
        context.update(kwargs)
        return super().get_context_data(**context)

    def get_log_type(self):
        if self.log_type is None:
            raise ImproperlyConfigured("log_type is required")
        return self.log_type

    def get_log_count(self):
        if not self.log_count:
            self.log_count = self.get_queryset().count()

        return self.log_count

    def get_session_key(self):
        return f'data_log_{self.get_log_type()}_filters'

    def save_filters(self, form):
        self.request.session[self.get_session_key()] = {}
        for key, value in form.data.lists():
            if key in form.base_fields and value[0]:
                self.request.session[self.get_session_key()][key] = value

    def get_filters(self):
        # Only retrieve filter keys used by the current form
        filter_data = self.request.session.get(self.get_session_key(), {})
        return {
            k: v for k, v in filter_data.items() if k in self.get_form_class().base_fields
        }

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


class DashboardView(DataLogView):
    pass


class DetailView(DataLogView):
    pass


class TableView(DataLogView, ListView):
    form_class = FilterLogTimestamp
    paginate_by = 50
    context_object_name = 'logs'


# Dungeons
class DungeonMixin:
    log_type = 'dungeonlog'
    form_class = FilterDungeonLogForm

    def get_success_rate(self):
        if self.get_log_count():
            success_count = self.get_queryset().filter(success=True).count()
            return float(success_count) / self.get_log_count() * 100

    def get_queryset(self):
        # Do not include incomplete logs
        qs = super().get_queryset()
        return qs.filter(success__isnull=False)

    def get_context_data(self, **kwargs):
        context = {
            'success_rate': self.get_success_rate()
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class DungeonDashboard(DungeonMixin, DashboardView):
    template_name = 'herders/profile/data_logs/dungeons/summary.html'

    def get_queryset(self):
        # Do not include incomplete logs
        qs = super().get_queryset()
        return qs.filter(success__isnull=False)

    def get_context_data(self, **kwargs):
        qs = self.get_queryset()
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

        kwargs['dashboard'] = dashboard_data
        kwargs['success_rate'] = success_rate
        kwargs['level_list'] = level_list

        return super().get_context_data(**kwargs)


class DungeonDetail(DungeonMixin, DetailView):
    template_name = 'herders/profile/data_logs/dungeons/detail.html'
    form_class = FilterLogTimestamp  # When viewing specific level, timestamp is only filter required
    dungeon = None
    level = None

    def get_queryset(self):
        return super().get_queryset().filter(level=self.level)

    def get_context_data(self, **kwargs):
        context = {
            'dungeon': self.get_dungeon(),
            'level': self.get_level(),
            'report': level_drop_report(self.get_queryset()),
            'start_date': self.get_queryset().last().timestamp if self.get_log_count() else None,
            'end_date': self.get_queryset().first().timestamp if self.get_log_count() else None,
        }

        context.update(kwargs)
        return super().get_context_data(**context)

    def get_dungeon(self):
        if self.dungeon:
            return self.dungeon

        dungeon_slug = self.kwargs.get('slug')
        if dungeon_slug:
            try:
                self.dungeon = Dungeon.objects.get(slug=dungeon_slug)
                return self.dungeon
            except Dungeon.DoesNotExist:
                raise Http404('Dungeon not found')
        else:
            raise Http404('No slug provided to locate dungeon')

    def get_level(self):
        if self.level:
            return self.level

        floor = self.kwargs.get('floor')
        difficulty = self.kwargs.get('difficulty')

        level = None
        levels = self.get_dungeon().level_set.all()

        if difficulty:
            difficulty_id = {v.lower(): k for k, v in dict(Level.DIFFICULTY_CHOICES).items()}.get(difficulty)

            if difficulty_id is None:
                raise Http404()

            levels = levels.filter(difficulty=difficulty_id)

        if floor:
            levels = levels.filter(floor=floor)
        else:
            # Pick first hell level for scenarios, otherwise always last level
            if self.get_dungeon().category == Dungeon.CATEGORY_SCENARIO:
                level = levels.filter(difficulty=Level.DIFFICULTY_HELL).first()
            else:
                level = levels.last()

        if not level:
            # Default to first level for all others
            level = levels.first()

        if not level:
            raise Http404('Level not found')

        self.level = level
        return level


class DungeonTable(DungeonMixin, TableView):
    template_name = 'herders/profile/data_logs/dungeons/table.html'


class ElementalRiftBeastTable(TableView):
    log_type = 'riftdungeonlog'
    template_name = 'herders/profile/data_logs/rift_beast.html'


class RiftRaidTable(TableView):
    log_type = 'riftraidlog'
    template_name = 'herders/profile/data_logs/rift_raid.html'


class WorldBossTable(TableView):
    log_type = 'worldbosslog'
    template_name = 'herders/profile/data_logs/world_boss.html'


class SummonsTable(TableView):
    log_type = 'summonlog'
    form_class = FilterSummonLogForm
    template_name = 'herders/profile/data_logs/summons.html'


class MagicShopTable(TableView):
    log_type = 'shoprefreshlog'
    template_name = 'herders/profile/data_logs/magic_shop.html'


class WishesTable(TableView):
    log_type = 'wishlog'
    template_name = 'herders/profile/data_logs/wish.html'


class RuneCraftingTable(TableView):
    log_type = 'craftrunelog'
    template_name = 'herders/profile/data_logs/rune_crafting.html'


class MagicBoxCraftingTable(TableView):
    log_type = 'magicboxcraft'
    template_name = 'herders/profile/data_logs/magic_box.html'
