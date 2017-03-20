from django.db.models import Q
import django_filters

from bestiary.models import Monster, Effect, Skill, LeaderSkill, ScalingStat
from .models import MonsterInstance, MonsterTag, RuneInstance


class MonsterInstanceFilter(django_filters.FilterSet):
    monster__name = django_filters.MethodFilter(action='filter_monster__name')
    tags__pk = django_filters.MultipleChoiceFilter(choices=MonsterTag.objects.values_list('pk', 'name'), conjoined=True)
    monster__element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    monster__archetype = django_filters.MultipleChoiceFilter(choices=Monster.TYPE_CHOICES)
    priority = django_filters.MultipleChoiceFilter(choices=MonsterInstance.PRIORITY_CHOICES)
    monster__leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=LeaderSkill.ATTRIBUTE_CHOICES)
    monster__leader_skill__area = django_filters.MultipleChoiceFilter(choices=LeaderSkill.AREA_CHOICES)
    monster__skills__scaling_stats__pk = django_filters.MultipleChoiceFilter(choices=ScalingStat.objects.values_list('pk', 'stat'), conjoined=True)
    monster__skills__skill_effect__pk = django_filters.MethodFilter(action='filter_monster__skills__skill_effect__pk')
    effects_logic = django_filters.MethodFilter()
    monster__fusion_food = django_filters.MethodFilter(action='filter_monster__fusion_food')

    class Meta:
        model = MonsterInstance
        fields = {
            'monster__name': ['exact'],
            'tags__pk': ['exact'],
            'stars': ['gte', 'lte'],
            'level': ['gte', 'lte'],
            'monster__element': ['exact'],
            'monster__archetype': ['exact'],
            'priority': ['exact'],
            'monster__is_awakened': ['exact'],
            'monster__leader_skill__attribute': ['exact'],
            'monster__leader_skill__area': ['exact'],
            'monster__skills__skill_effect__pk': ['exact'],
            'monster__skills__scaling_stats__pk': ['exact'],
            'effects_logic': ['exact'],
            'fodder': ['exact'],
            'in_storage': ['exact'],
            'monster__fusion_food': ['exact'],
        }

    def filter_monster__name(self, queryset, value):
        if value:
            return queryset.filter(Q(monster__name__icontains=value) | Q(monster__awakens_from__name__icontains=value))
        else:
            return queryset

    def filter_monster__fusion_food(self, queryset, value):
        if value:
            return queryset.filter(monster__fusion_food=True).exclude(ignore_for_fusion=True)
        else:
            return queryset.filter(Q(monster__fusion_food=False) | Q(ignore_for_fusion=True))

    def filter_monster__skills__skill_effect__pk(self, queryset, value):
        old_filtering = self.form.cleaned_data.get('effects_logic', False)
        stat_scaling = self.form.cleaned_data.get('monster__skills__scaling_stats__pk', [])

        if old_filtering:
            # Filter if any skill on the monster has the designated fields
            for pk in value:
                queryset = queryset.filter(monster__skills__skill_effect=pk)

            for pk in stat_scaling:
                queryset = queryset.filter(monster__skills__scaling_stats=pk)

            return queryset.distinct()

        else:
            # Filter effects based on effects of each individual skill. This ensures a monster will not show up unless it has
            # the desired effects on the same skill rather than across any skills.

            skills = Skill.objects.all()

            for pk in value:
                skills = skills.filter(skill_effect=pk)

            for pk in stat_scaling:
                skills = skills.filter(scaling_stats=pk)

            return queryset.filter(monster__skills__in=skills).distinct()

    def filter_effects_logic(self, queryset, value):
        # This field is just used to alter the logic of skill effect filter and is used in filter_monster__skills__skill_effect__pk()
        return queryset


class RuneInstanceFilter(django_filters.FilterSet):
    type = django_filters.MultipleChoiceFilter(choices=RuneInstance.TYPE_CHOICES)
    slot = django_filters.MultipleChoiceFilter(choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)))
    quality = django_filters.MultipleChoiceFilter(choices=RuneInstance.QUALITY_CHOICES)
    original_quality = django_filters.MultipleChoiceFilter(choices=RuneInstance.QUALITY_CHOICES)
    main_stat = django_filters.MultipleChoiceFilter(choices=RuneInstance.STAT_CHOICES)
    innate_stat = django_filters.MultipleChoiceFilter(choices=RuneInstance.STAT_CHOICES)
    substats = django_filters.MethodFilter()
    substat_logic = django_filters.MethodFilter()
    assigned_to = django_filters.MethodFilter(action='filter_assigned_to')

    class Meta:
        model = RuneInstance
        fields = {
            'type': ['exact'],
            'level': ['gte', 'lte'],
            'stars': ['gte', 'lte'],
            'slot': ['exact'],
            'quality': ['exact'],
            'original_quality': ['exact'],
            'assigned_to': ['exact'],
            'main_stat': ['exact'],
            'innate_stat': ['exact'],
            'marked_for_sale': ['exact'],
        }

    def filter_substats(self, queryset, value):
        any_substat = self.form.cleaned_data.get('substat_logic', False)

        if len(value):
            if any_substat:
                return queryset.filter(substats__overlap=value)
            else:
                return queryset.filter(substats__contains=value)
        else:
            return queryset

    def filter_substat_logic(self, queryset, value):
        # This field is just used to alter the logic of substat filter
        return queryset

    def filter_assigned_to(self, queryset, value):
        return queryset.filter(assigned_to__isnull=not value)
