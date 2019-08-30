from dal import autocomplete
from django.db.models import Q
from django.template import loader

from .models import Monster, Dungeon, GameItem


class BestiaryAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 15
    queryset = Monster.objects.all()

    def get_queryset(self):
        qs = super().get_queryset().filter(obtainable=True).order_by('family_id', 'element', 'is_awakened')

        if self.q:
            # Split the terms into words and build a Q object
            search_terms = self.q.split(' ')
            query = Q()

            for term in search_terms:
                query.add(
                    Q(name__icontains=term) |
                    Q(awakens_from__name__icontains=term) |
                    Q(awakens_to__name__icontains=term) |
                    Q(element__startswith=term),
                    Q.AND
                )

            qs = qs.filter(query)

        return qs

    def get_result_label(self, item):
        return loader.get_template('autocomplete/monster_choice.html').render({'choice': item})


class QuickSearchAutocomplete(BestiaryAutocomplete):
    def get_result_label(self, item):
        return loader.get_template('autocomplete/bestiary_link.html').render({'choice': item})


class DungeonAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 15
    qs = Dungeon.objects.all()

    def get_queryset(self):
        qs = super().get_queryset().filter(enabled=True).exclude(category=Dungeon.CATEGORY_SECRET)

        if self.q:
            # Split the terms into words and build a Q object
            search_terms = self.q.split(' ')
            query = Q()

            for term in search_terms:
                query.add(
                    Q(name__icontains=term),
                    Q.AND
                )

            qs = qs.filter(query)

        return qs

    def get_result_label(self, item):
        return loader.get_template('autocomplete/dungeon_choice.html').render({'choice': item})


class GameItemAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 15
    queryset = GameItem.objects.all()

    def get_queryset(self):
        qs = super().get_queryset()

        if self.q:
            # Split the terms into words and build a Q object
            search_terms = self.q.split(' ')
            query = Q()

            for term in search_terms:
                query.add(
                    Q(name__icontains=term),
                    Q.AND
                )

            qs = qs.filter(query)

        return qs