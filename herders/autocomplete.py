from django.db.models import Q
from django.template import loader

from dal import autocomplete

from .models import MonsterTag, MonsterInstance


class MonsterInstanceAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 15

    def get_queryset(self):
        qs = MonsterInstance.objects.filter(owner__user=self.request.user)

        if self.q:
            # Split the terms into words and build a Q object
            search_terms = self.q.split(' ')
            query = Q()

            for term in search_terms:
                query.add(
                    Q(monster__name__icontains=term) |
                    Q(monster__awakens_from__name__icontains=term) |
                    Q(monster__awakens_to__name__icontains=term) |
                    Q(monster__element__startswith=term),
                    Q.AND
                )

            qs = qs.filter(query)

        return qs

    def get_result_label(self, item):
        return loader.get_template('autocomplete/monster_instance_choice.html').render({'choice': item})

class MonsterTagAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 15

    def get_queryset(self):
        qs = MonsterTag.objects.all()

        if self.q:
            # Filter the queryset
            pass  # TODO: Figure out how the hell DAL handles multi word queries

        return qs
