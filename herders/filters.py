import django_filters

from .models import RuneInstance


class RuneInstanceFilter(django_filters.FilterSet):
    type = django_filters.MultipleChoiceFilter(choices=RuneInstance.TYPE_CHOICES)

    class Meta:
        model = RuneInstance
        fields = {
            'type': ['exact'],
            'level': ['gte'],
            'stars': ['gte'],
        }
        order_by = ['type', '-stars', '-level']
