from dal import autocomplete
from django.db.models import Q
from django.template import loader

from .models import Monster, Dungeon, GameItem


class FilterMultipleAutocompleteView(autocomplete.Select2QuerySetView):
    filter_fields = []

    def get_queryset(self):
        qs = self.queryset

        if self.q:
            # Split the terms into words and build a Q object
            search_terms = self.q.split(' ')
            query = Q()

            for term in search_terms:
                fields_query = Q()

                for field in self.filter_fields:
                    fields_query.add(Q(**{field: term}), Q.OR)

                query.add(fields_query, Q.AND)

            qs = qs.filter(query)

        return qs


class BestiaryAutocomplete(FilterMultipleAutocompleteView):
    paginate_by = 15
    queryset = Monster.objects.filter(obtainable=True).order_by('family_id', 'element', 'is_awakened')
    filter_fields = [
        'name__icontains',
        'awakens_from__name__icontains',
        'awakens_from__awakens_from__name__icontains',
        'awakens_to__name__icontains',
        'element__istartswith',
    ]

    def get_result_label(self, item):
        return loader.get_template('autocomplete/monster_choice.html').render({'choice': item})


class QuickSearchAutocomplete(BestiaryAutocomplete):
    def get_result_label(self, item):
        return loader.get_template('autocomplete/bestiary_link.html').render({'choice': item})
