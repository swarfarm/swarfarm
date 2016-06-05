from django.db.models import Q
import django_filters

from bestiary.models import Monster, Effect, Skill, LeaderSkill
from .models import MonsterInstance, MonsterTag, RuneInstance


class MonsterFilter(django_filters.FilterSet):
    base_stars = django_filters.MultipleChoiceFilter(choices=Monster.STAR_CHOICES)
    element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    archetype = django_filters.MultipleChoiceFilter(choices=Monster.TYPE_CHOICES)
    leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=LeaderSkill.ATTRIBUTE_CHOICES)
    leader_skill__area = django_filters.MultipleChoiceFilter(choices=LeaderSkill.AREA_CHOICES)
    skills__skill_effect__pk = django_filters.MethodFilter(action='filter_skills__skill_effect__pk')

    class Meta:
        model = Monster
        fields = {
            'name': ['icontains'],
            'element': ['exact'],
            'archetype': ['exact'],
            'base_stars': ['exact'],
            'is_awakened': ['exact'],
            'leader_skill__attribute': ['exact'],
            'leader_skill__area': ['exact'],
            'skills__skill_effect__pk': ['exact'],
            'fusion_food': ['exact'],
        }

    def filter_skills__skill_effect__pk(self, queryset, value):
        # Filter effects based on effects of each individual skill. This ensures a monster will not show up unless it has
        # the desired effects on the same skill rather than across any skills.

        skills = Skill.objects.all()

        for pk in value:
            skills = skills.filter(skill_effect__pk=pk)

        return queryset.filter(skills__in=skills).distinct()


class MonsterInstanceFilter(django_filters.FilterSet):
    tags__pk = django_filters.MultipleChoiceFilter(choices=MonsterTag.objects.values_list('pk', 'name'), conjoined=True)
    stars = django_filters.MultipleChoiceFilter(choices=Monster.STAR_CHOICES)
    monster__element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    monster__archetype = django_filters.MultipleChoiceFilter(choices=Monster.TYPE_CHOICES)
    priority = django_filters.MultipleChoiceFilter(choices=MonsterInstance.PRIORITY_CHOICES)
    monster__leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=LeaderSkill.ATTRIBUTE_CHOICES)
    monster__leader_skill__area = django_filters.MultipleChoiceFilter(choices=LeaderSkill.AREA_CHOICES)
    monster__skills__skill_effect__pk = django_filters.MethodFilter(action='filter_monster__skills__skill_effect__pk') # django_filters.MultipleChoiceFilter(choices=Effect.objects.all().values_list('pk', 'name'), conjoined=True)
    monster__fusion_food = django_filters.MethodFilter(action='filter_monster__fusion_food')

    class Meta:
        model = MonsterInstance
        fields = {
            'monster__name': ['icontains'],
            'tags__pk': ['exact'],
            'stars': ['exact'],
            'monster__element': ['exact'],
            'monster__archetype': ['exact'],
            'priority': ['exact'],
            'monster__is_awakened': ['exact'],
            'monster__leader_skill__attribute': ['exact'],
            'monster__leader_skill__area': ['exact'],
            'monster__skills__skill_effect__pk': ['exact'],
            'fodder': ['exact'],
            'in_storage': ['exact'],
            'monster__fusion_food': ['exact'],
        }

    def filter_monster__fusion_food(self, queryset, value):
        if value:
            return queryset.filter(monster__fusion_food=True).exclude(ignore_for_fusion=True)
        else:
            return queryset.filter(Q(monster__fusion_food=False) | Q(ignore_for_fusion=True))

    def filter_monster__skills__skill_effect__pk(self, queryset, value):
        # Filter effects based on effects of each individual skill. This ensures a monster will not show up unless it has
        # the desired effects on the same skill rather than across any skills.

        skills = Skill.objects.all()

        for pk in value:
            skills = skills.filter(skill_effect__pk=pk)

        return queryset.filter(monster__skills__in=skills).distinct()


class RuneInstanceFilter(django_filters.FilterSet):
    type = django_filters.MultipleChoiceFilter(choices=RuneInstance.TYPE_CHOICES)
    main_stat = django_filters.MultipleChoiceFilter(choices=RuneInstance.STAT_CHOICES)
    assigned_to = django_filters.MethodFilter(action='filter_assigned_to')

    class Meta:
        model = RuneInstance
        fields = {
            'type': ['exact'],
            'level': ['gte', 'lte'],
            'stars': ['gte', 'lte'],
            'slot': ['exact'],
            'assigned_to': ['exact'],
            'main_stat': ['exact'],
            'has_hp': ['exact'],
            'has_def': ['exact'],
            'has_atk': ['exact'],
            'has_crit_rate': ['exact'],
            'has_crit_dmg': ['exact'],
            'has_speed': ['exact'],
            'has_resist': ['exact'],
            'has_accuracy': ['exact'],
            'marked_for_sale': ['exact'],
        }

    def filter_assigned_to(self, queryset, value):
        return queryset.filter(assigned_to__isnull=not value)
