from dal import autocomplete
from django.db.models import Q
from django.template import loader

from .models import MonsterTag, MonsterInstance, RuneInstanceTag


class MonsterInstanceAutocomplete(autocomplete.Select2QuerySetView):
    queryset = MonsterInstance.objects.all()
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().filter(owner__user=self.request.user)

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
            qs = qs.filter(name__icontains=self.q)

        return qs


class RuneInstanceTagAutocomplete(autocomplete.Select2QuerySetView):
    queryset = RuneInstanceTag.objects.all()
    model_field_name = 'name'
    paginate_by = 15

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return super().get_queryset().none()

        return super().get_queryset().filter(owner__user=self.request.user)
