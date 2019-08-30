from bestiary.autocomplete import GameItemAutocomplete
from .models import SummonLog

# List summon item types on process start, not every query
summon_items = SummonLog.objects.values_list('item', flat=True)


class SummonItemAutocomplete(GameItemAutocomplete):
    def get_queryset(self):
        return super().get_queryset().filter(pk__in=summon_items)
