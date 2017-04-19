from django.contrib.staticfiles.templatetags.staticfiles import static
from django.db.models import Q
from django.urls import reverse

from rest_framework import serializers, viewsets, renderers, pagination

from .models import MonsterTag, MonsterInstance


class MonsterInstanceAutocompletePagination(pagination.PageNumberPagination):
    page_size = 30
    max_page_size = 30


class MonsterInstanceAutocompleteSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()
    image_filename = serializers.SerializerMethodField()

    class Meta:
        model = MonsterInstance
        fields = [
            'id',
            'url',
            'text',
            'image_filename',
            'stars',
            'level',
        ]

    def get_url(self, instance):
        return reverse('herders:monster_instance_view', kwargs={
            'profile_name': instance.owner.user.username,
            'instance_id': instance.pk.hex,
        })

    def get_text(self, instance):
        return str(instance)

    def get_image_filename(self, instance):
        return static('/herders/images/monsters/{}'.format(instance.monster.image_filename))


class MonsterInstanceAutocomplete(viewsets.ReadOnlyModelViewSet):
    renderer_classes = [renderers.JSONRenderer]
    serializer_class = MonsterInstanceAutocompleteSerializer
    pagination_class = MonsterInstanceAutocompletePagination

    def get_queryset(self):
        if self.request.user.is_authenticated:
            qs = MonsterInstance.objects.filter(owner=self.request.user.summoner).select_related('monster')
            search_terms = self.request.query_params.get('search')

            if search_terms:
                # Split the terms into words and build a Q object
                search_terms = search_terms.split(' ')
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
        else:
            qs = MonsterInstance.objects.none()

        return qs


class MonsterTagAutocomplete(viewsets.ReadOnlyModelViewSet):
    queryset = MonsterTag.objects.all()


# class MonsterInstanceAutocomplete(autocomplete.Select2QuerySetView):
#     paginate_by = 15
#
#     def get_queryset(self):
#         qs = MonsterInstance.objects.filter(owner__user=self.request.user)
#
#         if self.q:
#             # Split the terms into words and build a Q object
#             search_terms = self.q.split(' ')
#             query = Q()
#
#             for term in search_terms:
#                 query.add(
#                     Q(name__icontains=term) |
#                     Q(awakens_from__name__icontains=term) |
#                     Q(awakens_to__name__icontains=term) |
#                     Q(element__startswith=term),
#                     Q.AND
#                 )
#
#             qs = qs.filter(query)
#
#         return qs
#
#     def get_result_value(self, result):
#         return result.pk.hex
#
#
# class MonsterTagAutocomplete(autocomplete.Select2QuerySetView):
#     paginate_by = 15
#
#     def get_queryset(self):
#         qs = MonsterTag.objects.all()
#
#         if self.q:
#             # Filter the queryset
#             pass  # TODO: Figure out how the hell DAL handles multi word queries
#
#         return qs


# Old DAL implementation
# class MonsterInstanceAutocomplete(autocomplete_light.AutocompleteModelTemplate):
#     model = MonsterInstance
#     search_fields = ['monster__name', 'monster__awakens_from__name', 'monster__awakens_to__name', '^monster__element']
#     split_words = True
#     choice_template = 'autocomplete/monster_instance_choice.html'
#     limit_choices = 15
#     attrs = {
#         'placeholder': 'Start typing monster name',
#         'data-autocomplete-minimum-characters': 2,
#     }
#
#     def choices_for_request(self):
#         self.choices = self.choices.filter(owner=self.request.user.summoner)
#         monster_filter = self.request.GET.get('monster', None)
#
#         # set .data of input autocomplete to {monster: <<id>>} in javascript to add query parameter
#         # See line 265 autocomplete.js
#
#         if monster_filter:
#             self.choices = self.choices.filter(monster__pk=monster_filter)
#
#         return super(MonsterInstanceAutocomplete, self).choices_for_request()
#
# autocomplete_light.register(MonsterInstanceAutocomplete)
#
#
# class MonsterTagAutocomplete(autocomplete_light.AutocompleteModelTemplate):
#     model = MonsterTag
#     search_fields = ['name']
#     split_words = True
#     choice_template = 'autocomplete/monster_tag_choice.html'
#     limit_choices = 15
#     attrs = {
#         'placeholder': 'Start typing...',
#         'data-autocomplete-minimum-characters': 0,
#     }
#
# autocomplete_light.register(MonsterTagAutocomplete)