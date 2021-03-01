import django_filters
from django.contrib.auth.models import User
from django.db.models import Q

from bestiary.models import Monster, Skill, SkillEffect, LeaderSkill, ScalingStat
from .models import ArtifactInstance, MonsterInstance, MonsterTag, RuneInstance, Team


class SummonerFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {
            'username': ['exact'],
            'summoner__server': ['exact']
        }


class MonsterInstanceFilter(django_filters.FilterSet):
    monster = django_filters.NumberFilter()
    monster__name = django_filters.CharFilter(method='filter_monster__name')
    tags__pk = django_filters.ModelMultipleChoiceFilter(queryset=MonsterTag.objects.all(), to_field_name='pk', conjoined=True)
    monster__element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    monster__archetype = django_filters.MultipleChoiceFilter(choices=Monster.ARCHETYPE_CHOICES)
    monster__awaken_level = django_filters.MultipleChoiceFilter(choices=Monster.AWAKEN_CHOICES)
    priority = django_filters.MultipleChoiceFilter(choices=MonsterInstance.PRIORITY_CHOICES)
    monster__leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=LeaderSkill.ATTRIBUTE_CHOICES)
    monster__leader_skill__area = django_filters.MultipleChoiceFilter(choices=LeaderSkill.AREA_CHOICES)
    monster__skills__scaling_stats__pk = django_filters.ModelMultipleChoiceFilter(queryset=ScalingStat.objects.all(), to_field_name='pk', conjoined=True)
    monster__skills__effect__pk = django_filters.ModelMultipleChoiceFilter(queryset=SkillEffect.objects.all(), method='filter_monster__skills__effect__pk')
    monster__skills__passive = django_filters.BooleanFilter(method='filter_monster_skills_passive')
    effects_logic = django_filters.BooleanFilter(method='filter_effects_logic')
    monster__fusion_food = django_filters.BooleanFilter(method='filter_monster__fusion_food')

    class Meta:
        model = MonsterInstance
        fields = {
            'monster': ['exact'],
            'monster__name': ['exact'],
            'tags__pk': ['exact'],
            'stars': ['gte', 'lte'],
            'level': ['gte', 'lte'],
            'monster__element': ['exact'],
            'monster__archetype': ['exact'],
            'priority': ['exact'],
            'monster__awaken_level': ['exact'],
            'monster__leader_skill__attribute': ['exact'],
            'monster__leader_skill__area': ['exact'],
            'monster__skills__effect__pk': ['exact'],
            'monster__skills__scaling_stats__pk': ['exact'],
            'monster__skills__passive': ['exact'],
            'effects_logic': ['exact'],
            'fodder': ['exact'],
            'in_storage': ['exact'],
            'monster__fusion_food': ['exact'],
        }

    def filter_monster__name(self, queryset, name, value):
        if value:
            return queryset.filter(monster__name__istartswith=value)
        else:
            return queryset

    def filter_monster__fusion_food(self, queryset, name, value):
        if value:
            return queryset.filter(monster__fusion_food=True).exclude(ignore_for_fusion=True)
        else:
            return queryset.filter(Q(monster__fusion_food=False) | Q(ignore_for_fusion=True))

    def filter_monster__skills__effect__pk(self, queryset, name, value):
        old_filtering = self.form.cleaned_data.get('effects_logic', False)
        stat_scaling = self.form.cleaned_data.get('monster__skills__scaling_stats__pk', [])
        passive = self.form.cleaned_data.get('monster__skills__passive', None)

        if old_filtering:
            # Filter if any skill on the monster has the designated fields
            for effect in value:
                queryset = queryset.filter(monster__skills__effect=effect)

            for pk in stat_scaling:
                queryset = queryset.filter(monster__skills__scaling_stats=pk)

            if passive is not None:
                queryset = queryset.filter(
                    monster__skills__passive=passive,
                )

            return queryset.distinct()

        else:
            # Filter effects based on effects of each individual skill. This ensures a monster will not show up unless it has
            # the desired effects on the same skill rather than across any skills.

            skills = Skill.objects.all()

            for effect in value:
                skills = skills.filter(effect=effect)

            for pk in stat_scaling:
                skills = skills.filter(scaling_stats=pk)

            if passive is not None:
                skills = skills.filter(
                    passive=passive,
                )

            return queryset.filter(monster__skills__in=skills).distinct()

    def filter_effects_logic(self, queryset, name, value):
        # This field is just used to alter the logic of skill effect filter and is used in filter_monster__skills__effect__pk()
        return queryset


class RuneInstanceFilter(django_filters.FilterSet):
    type = django_filters.MultipleChoiceFilter(choices=RuneInstance.TYPE_CHOICES)
    slot = django_filters.MultipleChoiceFilter(choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)))
    quality = django_filters.MultipleChoiceFilter(choices=RuneInstance.QUALITY_CHOICES)
    original_quality = django_filters.MultipleChoiceFilter(choices=RuneInstance.QUALITY_CHOICES)
    main_stat = django_filters.MultipleChoiceFilter(choices=RuneInstance.STAT_CHOICES)
    innate_stat = django_filters.MultipleChoiceFilter(choices=RuneInstance.STAT_CHOICES)
    substats = django_filters.MultipleChoiceFilter(choices=RuneInstance.STAT_CHOICES, method='filter_substats')
    substat_logic = django_filters.BooleanFilter(method='filter_substat_logic')
    assigned_to = django_filters.BooleanFilter(method='filter_assigned_to')

    class Meta:
        model = RuneInstance
        fields = {
            'type': ['exact'],
            'level': ['exact', 'lte', 'lt', 'gte', 'gt'],
            'stars': ['exact', 'lte', 'lt', 'gte', 'gt'],
            'slot': ['exact'],
            'quality': ['exact'],
            'original_quality': ['exact'],
            'ancient': ['exact'],
            'assigned_to': ['exact'],
            'main_stat': ['exact'],
            'innate_stat': ['exact'],
            'marked_for_sale': ['exact'],
            'has_grind': ['exact', 'lte', 'lt', 'gte', 'gt'],
            'has_gem': ['exact'],
        }

    def filter_substats(self, queryset, name, value):
        any_substat = self.form.cleaned_data.get('substat_logic', False)

        if len(value):
            if any_substat:
                return queryset.filter(substats__overlap=value)
            else:
                return queryset.filter(substats__contains=value)
        else:
            return queryset

    def filter_substat_logic(self, queryset, name, value):
        # This field is just used to alter the logic of substat filter
        return queryset

    def filter_assigned_to(self, queryset, name, value):
        return queryset.filter(assigned_to__isnull=not value)


class TeamFilter(django_filters.FilterSet):
    class Meta:
        model = Team
        fields = {
            'name': ['exact', 'istartswith', 'icontains'],
            'description': ['icontains']
        }

class ArtifactInstanceFilter(django_filters.FilterSet):
    slot = django_filters.MultipleChoiceFilter(
        method='filter_slot',
        choices=ArtifactInstance.NORMAL_ELEMENT_CHOICES + ArtifactInstance.ARCHETYPE_CHOICES
    )
    main_stat = django_filters.MultipleChoiceFilter(choices=ArtifactInstance.MAIN_STAT_CHOICES)
    quality = django_filters.MultipleChoiceFilter(choices=ArtifactInstance.QUALITY_CHOICES)
    original_quality = django_filters.MultipleChoiceFilter(choices=ArtifactInstance.QUALITY_CHOICES)
    effects = django_filters.MultipleChoiceFilter(method='filter_effects', choices=ArtifactInstance.EFFECT_CHOICES)
    effects_logic = django_filters.BooleanFilter(method='filter_bypass')
    assigned_to = django_filters.BooleanFilter(method='filter_assigned_to')

    class Meta:
        model = ArtifactInstance
        fields = {
            'main_stat': ['exact'],
            'level': ['exact', 'lte', 'lt', 'gte', 'gt'],
            'quality': ['exact', 'in'],
            'original_quality': ['exact', 'in'],
            'efficiency': ['exact', 'lt', 'gt', 'lte', 'gte'],
            'assigned_to': ['exact'],
        }

    def filter_slot(self, queryset, name, value):
        # Split slot filter value into element/archetype fields and filter on both
        all_elements = [choice[0] for choice in ArtifactInstance.NORMAL_ELEMENT_CHOICES]
        all_archetypes = [choice[0] for choice in ArtifactInstance.ARCHETYPE_CHOICES]

        elements = []
        archetypes = []
        for s in value:
            if s in all_elements:
                elements.append(s)
            elif s in all_archetypes:
                archetypes.append(s)

        return queryset.filter(Q(element__in=elements) | Q(archetype__in=archetypes))

    def filter_effects(self, queryset, name, value):
        any_effect = self.form.cleaned_data.get('effects_logic', False)

        if len(value):
            if any_effect:
                return queryset.filter(effects__overlap=value)
            else:
                return queryset.filter(effects__contains=value)
        else:
            return queryset

    def filter_assigned_to(self, queryset, name, value):
        return queryset.filter(assigned_to__isnull=not value)

    def filter_bypass(self, queryset, name, value):
        return queryset