import django_filters

from .models import Monster, MonsterInstance, MonsterSkill, MonsterSkillEffect, MonsterLeaderSkill, RuneInstance


class MonsterInstanceFilter(django_filters.FilterSet):
    stars = django_filters.MultipleChoiceFilter(choices=Monster.STAR_CHOICES)
    monster__element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    monster__archetype = django_filters.MultipleChoiceFilter(choices=Monster.TYPE_CHOICES)
    priority = django_filters.MultipleChoiceFilter(choices=MonsterInstance.PRIORITY_CHOICES)
    monster__leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=MonsterLeaderSkill.ATTRIBUTE_CHOICES)

    class Meta:
        model = MonsterInstance
        fields = {
            'monster__name': ['icontains'],
            'stars': ['exact'],
            'monster__element': ['exact'],
            'monster__archetype': ['exact'],
            'priority': ['exact'],
            'monster__leader_skill__attribute': ['exact'],
        }


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
        }

    def filter_assigned_to(self, queryset, value):
        return queryset.filter(assigned_to__isnull=not value)
