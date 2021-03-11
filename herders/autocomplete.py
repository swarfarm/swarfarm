from django.db.models import Q
from django.db.models.query import QuerySet
from django.http.response import HttpResponseBadRequest
from django.template import loader

from dal import autocomplete

from .models import MonsterTag, MonsterInstance, Summoner


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


class MonsterInstanceFollowerAutocomplete(autocomplete.Select2QuerySetView):
    paginate_by = 15

    def get_queryset(self):
        follower_name = self.forwarded.get('follower_name', None)
        
        if not follower_name:
            return MonsterInstance.objects.none()

        summoner = self.request.user.summoner
        try:
            follower = Summoner.objects.select_related('user').get(user__username=follower_name)
        except Summoner.DoesNotExist:
            return MonsterInstance.objects.none()
            
        can_compare = (follower in summoner.following.all() and follower in summoner.followed_by.all() and follower.public)

        if not can_compare:
            return MonsterInstance.objects.none()
        
        qs = MonsterInstance.objects.filter(owner=follower)

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
