import django_filters

from .models import RuneInstance


class RuneInstanceFilter(django_filters.FilterSet):
    type = django_filters.MultipleChoiceFilter(choices=RuneInstance.TYPE_CHOICES)
    assigned_to = django_filters.MethodFilter(action='filter_assigned_to')

    class Meta:
        model = RuneInstance
        fields = {
            'type': ['exact'],
            'level': ['gte', 'lte'],
            'stars': ['gte', 'lte'],
            'slot': ['exact'],
            'assigned_to': ['exact'],
            'has_hp': ['exact'],
            'has_def': ['exact'],
            'has_crit_rate': ['exact'],
            'has_crit_dmg': ['exact'],
            'has_speed': ['exact'],
            'has_resist': ['exact'],
            'has_accuracy': ['exact'],
        }

    def filter_assigned_to(self, queryset, value):
        return queryset.filter(assigned_to__isnull=not value)
