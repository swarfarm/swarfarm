from django.db.models import Q

from bestiary.autocomplete import GameItemAutocomplete
from bestiary.models import GameItem

# List summon item types on process start, not every query
summon_category = Q(category=GameItem.CATEGORY_SUMMON_SCROLL)
summon_currency = Q(category=GameItem.CATEGORY_CURRENCY) & Q(com2us_id__in=[1, 2]) # Crystals and Social
summon_items = GameItem.objects.filter(summon_category | summon_currency)


class SummonItemAutocomplete(GameItemAutocomplete):
    def get_queryset(self):
        return super().get_queryset().filter(pk__in=summon_items)
