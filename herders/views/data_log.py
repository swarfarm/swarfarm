from datetime import datetime
from functools import reduce

from django.core.exceptions import ImproperlyConfigured
from django.db.models import Model, QuerySet, Q, F, Min, Max, Avg, Count, Sum, Value, CharField, Case, When
from django.db.models.functions import Concat
from django.http import Http404
from django.views.generic import FormView, ListView, TemplateView
from django_pivot.histogram import histogram

from bestiary.models import Dungeon, Level, GameItem, RuneCraft
from data_log.reports.generate import get_drop_querysets, drop_report, get_monster_report, get_rune_report
from data_log.util import transform_to_dict, replace_value_with_choice, floor_to_nearest, ceil_to_nearest
from herders.forms import FilterLogTimestamp, FilterDungeonLogForm, FilterRiftDungeonForm, FilterSummonLogForm, \
    FilterWorldBossLogForm, FilterRiftDungeonFormGradeOnly, FilterRiftRaidLogForm, FilterRuneCraftLogForm, FilterMagicBoxCraftLogForm
from herders.models import Monster, RuneInstance
from .base import SummonerMixin, OwnerRequiredMixin


class SectionMixin:
    def get_context_data(self, **kwargs):
        kwargs['view'] = 'data_log'
        kwargs['view_name'] = self.request.resolver_match.view_name

        return super().get_context_data(**kwargs)


# Generic views
class DataLogView(SectionMixin, SummonerMixin, OwnerRequiredMixin, FormView):
    log_type = None
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
        return self.get_filters()

    def form_valid(self, form):
        self.save_filters(form)

        return super().form_valid(form)

    def get_success_url(self):
        # Back to where it was POSTed from
        return self.request.path

    def get_queryset(self):
        qs = getattr(self.summoner, f'{self.get_log_type()}_set').all()
        query = Q()
        for key, value in self.get_filters().items():
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
            'records_limited': self.max_records and self.get_log_count() == self.max_records,
            'start_date': self.get_queryset().last().timestamp if self.get_log_count() else None,
            'end_date': self.get_queryset().first().timestamp if self.get_log_count() else None,
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
        for key, value in form.cleaned_data.items():
            if isinstance(value, QuerySet):
                # Save a list of the PK of the models
                value_to_store = list(value.values_list('pk', flat=True))
            elif isinstance(value, Model):
                # Save the PK of the model
                value_to_store = value.pk
            elif isinstance(value, datetime):
                value_to_store = value.isoformat()
            else:
                value_to_store = value

            if value_to_store is not None:
                self.request.session[self.get_session_key()][key] = value_to_store

    def get_filters(self):
        # Only retrieve filter keys used by the current form
        filter_data = self.request.session.get(self.get_session_key(), {})
        return {
            k: v for k, v in filter_data.items() if k in self.get_form_class().base_fields
        }


class DashboardMixin:
    pass


class DetailMixin:
    form_class = FilterLogTimestamp  # Only need timestamp filters when viewing detail. Other params are source from URL


class SuccessMixin:
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


class GradeMixin:
    def get_grade_statistics(self):
        return super().get_queryset().aggregate(min=Min('grade'), avg=Avg('grade'), max=Max('grade'))

    def get_context_data(self, **kwargs):
        context = {
            'grade_stats': self.get_grade_statistics()
        }
        context.update(**kwargs)
        return super().get_context_data(**context)


class TableView(DataLogView, ListView):
    paginate_by = 50
    context_object_name = 'logs'


# Home views
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


# Dungeons
class DungeonMixin(SuccessMixin):
    log_type = 'dungeonlog'
    form_class = FilterDungeonLogForm

    def get_queryset(self):
        # Do not include incomplete logs
        qs = super().get_queryset()
        return qs.filter(success__isnull=False)


class DungeonDashboard(DashboardMixin, DungeonMixin, DataLogView):
    template_name = 'herders/profile/data_logs/dungeons/dashboard.html'

    def get_context_data(self, **kwargs):
        all_drops = get_drop_querysets(self.get_queryset())
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

        dashboard_data = {
            'energy_spent': {
                'type': 'occurrences',
                'total': self.get_log_count(),
                'data': transform_to_dict(
                    list(
                        self.get_queryset().values(
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

        level_order = self.get_queryset().values('level').annotate(
            energy_spent=Sum('level__energy_cost')
        ).order_by('-energy_spent').values_list('level', flat=True)
        preserved_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(level_order)])
        level_list = Level.objects.filter(
            pk__in=set(self.get_queryset().values_list('level', flat=True))
        ).order_by(preserved_order).prefetch_related('dungeon')[:20]

        kwargs['dashboard'] = dashboard_data
        kwargs['level_list'] = level_list

        return super().get_context_data(**kwargs)


class DungeonDetail(DetailMixin, DungeonMixin, DataLogView):
    template_name = 'herders/profile/data_logs/dungeons/detail.html'
    dungeon = None
    level = None

    def get_queryset(self):
        return super().get_queryset().filter(level=self.get_level())

    def get_context_data(self, **kwargs):
        context = {
            'dungeon': self.get_dungeon(),
            'level': self.get_level(),
            'report': drop_report(self.get_queryset(), min_count=0),
        }

        context.update(kwargs)
        return super().get_context_data(**context)

    def get_dungeon(self):
        if not self.dungeon:
            dungeon_slug = self.kwargs.get('slug')
            if dungeon_slug:
                try:
                    self.dungeon = Dungeon.objects.get(slug=dungeon_slug)
                    return self.dungeon
                except Dungeon.DoesNotExist:
                    raise Http404('Dungeon not found')
            else:
                raise Http404('No slug provided to locate dungeon')
        return self.dungeon

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


# Elemental Rift Beast Dungeon
class ElementalRiftDungeonMixin(SuccessMixin, GradeMixin):
    log_type = 'riftdungeonlog'
    form_class = FilterRiftDungeonForm


class ElementalRiftDungeonDashboard(DashboardMixin, ElementalRiftDungeonMixin, DataLogView):
    template_name = 'herders/profile/data_logs/rift_dungeon/dashboard.html'

    def get_context_data(self, **kwargs):
        all_drops = get_drop_querysets(self.get_queryset())
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
        }

        dashboard_data = {
            'energy_spent': {
                'type': 'occurrences',
                'total': self.get_log_count(),
                'data': transform_to_dict(
                    list(
                        self.get_queryset().values(
                            'level__dungeon__name'
                        ).annotate(
                            count=Sum('level__energy_cost'),
                        ).order_by('-count')
                    ),
                    name_key='level__dungeon__name',
                ),
            },
            'recent_drops': recent_drops,
        }

        level_list = Level.objects.filter(
            pk__in=set(self.get_queryset().values_list('level', flat=True))
        )

        kwargs['dashboard'] = dashboard_data
        kwargs['level_list'] = level_list

        return super().get_context_data(**kwargs)


class ElementalRiftDungeonDetail(DashboardMixin, ElementalRiftDungeonMixin, DataLogView):
    form_class = FilterRiftDungeonFormGradeOnly
    template_name = 'herders/profile/data_logs/rift_dungeon/detail.html'
    dungeon = None
    level = None

    def get_queryset(self):
        return super().get_queryset().filter(level=self.get_level())

    def get_context_data(self, **kwargs):
        if self.get_log_count():
            bin_width = 50000
            damage_stats = self.get_queryset().aggregate(min=Min('total_damage'), max=Max('total_damage'))
            bin_start = floor_to_nearest(damage_stats['min'], bin_width)
            bin_end = ceil_to_nearest(damage_stats['max'], bin_width)
            damage_histogram = {
                'type': 'histogram',
                'width': bin_width,
                'data': histogram(self.get_queryset(), 'total_damage', range(bin_start, bin_end, bin_width)),
            }
        else:
            damage_histogram = None

        context = {
            'dungeon': self.get_dungeon(),
            'level': self.get_level(),
            'report': drop_report(self.get_queryset(), min_count=0),
            'damage_histogram': damage_histogram
        }

        context.update(kwargs)
        return super().get_context_data(**context)

    def get_dungeon(self):
        if not self.dungeon:
            dungeon_slug = self.kwargs.get('slug')
            if dungeon_slug:
                try:
                    self.dungeon = Dungeon.objects.get(slug=dungeon_slug)
                    return self.dungeon
                except Dungeon.DoesNotExist:
                    raise Http404('Dungeon not found')
            else:
                raise Http404('No slug provided to locate dungeon')
        return self.dungeon

    def get_level(self):
        if not self.level:
            self.level = self.get_dungeon().level_set.first()

        return self.level


class ElementalRiftBeastTable(ElementalRiftDungeonMixin, TableView):
    template_name = 'herders/profile/data_logs/rift_dungeon/table.html'


# Rift Raid
class RiftRaidMixin(SuccessMixin):
    log_type = 'riftraidlog'
    form_class = FilterRiftRaidLogForm


class RiftRaidDashboard(DashboardMixin, RiftRaidMixin, DataLogView):
    template_name = 'herders/profile/data_logs/rift_raid/dashboard.html'

    def get_context_data(self, **kwargs):
        all_drops = get_drop_querysets(self.get_queryset())
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
                {'element': Monster.ELEMENT_CHOICES}
            ) if 'monsters' in all_drops else [],
            'rune_crafts': replace_value_with_choice(
                list(all_drops['rune_crafts'].values(
                    'type',
                    'quality',
                    'rune',
                ).annotate(
                    count=Count('pk')
                ).order_by('-count') if 'rune_crafts' in all_drops else []),
                {
                    'type': RuneCraft.CRAFT_CHOICES,
                    'quality': RuneCraft.QUALITY_CHOICES,
                    'rune': RuneCraft.TYPE_CHOICES,
                }
            )
        }

        level_list = Level.objects.filter(
            pk__in=set(self.get_queryset().values_list('level', flat=True))
        ).order_by('-floor').prefetch_related('dungeon')

        kwargs['dashboard'] = {
            'recent_drops': recent_drops,
        }
        kwargs['level_list'] = level_list

        return super().get_context_data(**kwargs)


class RiftRaidDetail(DetailMixin, RiftRaidMixin, DataLogView):
    form_class = FilterLogTimestamp
    template_name = 'herders/profile/data_logs/rift_raid/detail.html'
    dungeon = None
    level = None

    def get_queryset(self):
        return super().get_queryset().filter(level=self.get_level())

    def get_context_data(self, **kwargs):
        if self.get_log_count():
            contribution_histogram = {
                'type': 'histogram',
                'width': 1,
                'data': histogram(self.get_queryset(), 'contribution_amount', range(0, 100)),
            }
        else:
            contribution_histogram = None

        context = {
            'dungeon': self.get_dungeon(),
            'level': self.get_level(),
            'report': drop_report(
                self.get_queryset(),
                min_count=0,
                include_currency=True,
                exclude_social_points=True,
                owner_only=True,
            ),
            'contribution_histogram': contribution_histogram
        }

        context.update(kwargs)
        return super().get_context_data(**context)

    def get_dungeon(self):
        if not self.dungeon:
            try:
                self.dungeon = Dungeon.objects.get(category=Dungeon.CATEGORY_RIFT_OF_WORLDS_RAID)
                return self.dungeon
            except Dungeon.DoesNotExist:
                raise Http404('Dungeon not found')

        return self.dungeon

    def get_level(self):
        if not self.level:
            floor = self.kwargs.get('floor')
            try:
                self.level = self.get_dungeon().level_set.get(floor=floor)
            except Model.DoesNotExist:
                raise Http404()

        return self.level


class RiftRaidTable(RiftRaidMixin, TableView):
    template_name = 'herders/profile/data_logs/rift_raid/table.html'


# World Boss
class WorldBossMixin(GradeMixin):
    log_type = 'worldbosslog'
    form_class = FilterWorldBossLogForm


class WorldBossDashboard(DashboardMixin, WorldBossMixin, DataLogView):
    template_name = 'herders/profile/data_logs/world_boss/dashboard.html'

    def get_context_data(self, **kwargs):
        all_drops = get_drop_querysets(self.get_queryset())
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
        }

        if self.get_log_count():
            bin_width = 50000
            damage_stats = self.get_queryset().aggregate(min=Min('damage'), max=Max('damage'))
            bin_start = floor_to_nearest(damage_stats['min'], bin_width)
            bin_end = ceil_to_nearest(damage_stats['max'], bin_width)
            damage_histogram = {
                'type': 'histogram',
                'width': bin_width,
                'data': histogram(self.get_queryset(), 'damage', range(bin_start, bin_end, bin_width)),
            }
        else:
            damage_histogram = None

        context = {
            'dashboard': {
                'recent_drops': recent_drops,
            },
            'report': drop_report(self.get_queryset(), min_count=0),
            'damage_histogram': damage_histogram
        }

        context.update(kwargs)
        return super().get_context_data(**context)


class WorldBossTable(WorldBossMixin, TableView):
    template_name = 'herders/profile/data_logs/world_boss/table.html'


# Summons
class SummonsMixin:
    log_type = 'summonlog'
    form_class = FilterSummonLogForm


class SummonsDashboard(DashboardMixin, SummonsMixin, DataLogView):
    template_name = 'herders/profile/data_logs/summons/dashboard.html'

    def get_context_data(self, **kwargs):
        dashboard_data = {
            'summons_performed': {
                'type': 'occurrences',
                'total': self.get_log_count(),
                'data': transform_to_dict(
                    list(self.get_queryset().values('item__name').annotate(count=Count('pk')).order_by('-count')),
                    name_key='item__name',
                ),
            }
        }

        item_list = GameItem.objects.filter(
            pk__in=set(self.get_queryset().values_list('item', flat=True))
        )

        context = {
            'dashboard': dashboard_data,
            'item_list': item_list,
        }

        context.update(kwargs)
        return super().get_context_data(**context)


class SummonsDetail(DetailMixin, SummonsMixin, DataLogView):
    template_name = 'herders/profile/data_logs/summons/detail.html'
    item = None

    def get_queryset(self):
        return super().get_queryset().filter(item=self.get_item())

    def get_item(self):
        if not self.item:
            slug = self.kwargs.get('slug')
            if slug:
                try:
                    self.item = GameItem.objects.get(slug=slug)
                except GameItem.DoesNotExist:
                    raise Http404()

        return self.item

    def get_context_data(self, **kwargs):
        context = {
            'item': self.get_item(),
            'report': get_monster_report(self.get_queryset(), self.get_log_count(), min_count=0)
        }

        context.update(kwargs)
        return super().get_context_data(**context)


class SummonsTable(SummonsMixin, TableView):
    template_name = 'herders/profile/data_logs/summons/table.html'


# Magic Shop
class MagicShopMixin:
    log_type = 'shoprefreshlog'
    form_class = FilterLogTimestamp


class MagicShopDashboard(DashboardMixin, MagicShopMixin, DataLogView):
    template_name = 'herders/profile/data_logs/magic_shop/dashboard.html'

    def get_context_data(self, **kwargs):
        context = {
            'report': drop_report(self.get_queryset(), min_count=0)
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class MagicShopTable(MagicShopMixin, TableView):
    template_name = 'herders/profile/data_logs/magic_shop/table.html'


# Wishes
class WishMixin:
    log_type = 'wishlog'
    form_class = FilterLogTimestamp


class WishDashboard(DashboardMixin, WishMixin, DataLogView):
    template_name = 'herders/profile/data_logs/wish/dashboard.html'

    def get_context_data(self, **kwargs):
        context = {
            'report': drop_report(self.get_queryset(), min_count=0, include_currency=True)
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class WishTable(WishMixin, TableView):
    template_name = 'herders/profile/data_logs/wish/table.html'


# Rune Crafting
class RuneCraftMixin:
    log_type = 'craftrunelog'
    form_class = FilterRuneCraftLogForm


class RuneCraftDashboard(DashboardMixin, RuneCraftMixin, DataLogView):
    template_name = 'herders/profile/data_logs/rune_craft/dashboard.html'

    def get_context_data(self, **kwargs):
        context = {
            'report': get_rune_report(self.get_queryset(), self.get_log_count(), min_count=0)
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class RuneCraftTable(RuneCraftMixin, TableView):
    template_name = 'herders/profile/data_logs/rune_crafting.html'


# Magic Box Crafting
class MagicBoxCraftMixin:
    log_type = 'magicboxcraft'
    form_class = FilterMagicBoxCraftLogForm


class MagicBoxCraftDashboard(DashboardMixin, MagicBoxCraftMixin, DataLogView):
    template_name = 'herders/profile/data_logs/magic_box/dashboard.html'

    def get_context_data(self, **kwargs):
        context = {
            'report': drop_report(self.get_queryset(), min_count=0, include_currency=True)
        }
        context.update(kwargs)
        return super().get_context_data(**context)


class MagicBoxCraftTable(MagicBoxCraftMixin, TableView):
    template_name = 'herders/profile/data_logs/magic_box/table.html'
