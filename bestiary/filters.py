from django.db.models import Q
import django_filters

from bestiary.models import Monster, Effect, Skill, LeaderSkill, ScalingStat


class MonsterFilter(django_filters.FilterSet):
    name = django_filters.MethodFilter(action='filter_name')
    element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    archetype = django_filters.MultipleChoiceFilter(choices=Monster.TYPE_CHOICES)
    leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=LeaderSkill.ATTRIBUTE_CHOICES)
    leader_skill__area = django_filters.MultipleChoiceFilter(choices=LeaderSkill.AREA_CHOICES)
    skills__scaling_stats__pk = django_filters.MultipleChoiceFilter(choices=ScalingStat.objects.values_list('pk', 'stat'), conjoined=True)
    effects_logic = django_filters.MethodFilter()
    skills__skill_effect__pk = django_filters.MethodFilter(action='filter_skills__skill_effect__pk')

    class Meta:
        model = Monster
        fields = {
            'name': ['exact'],
            'element': ['exact'],
            'archetype': ['exact'],
            'base_stars': ['lte', 'gte'],
            'is_awakened': ['exact'],
            'leader_skill__attribute': ['exact'],
            'leader_skill__area': ['exact'],
            'skills__skill_effect__pk': ['exact'],
            'skills__scaling_stats__pk': ['exact'],
            'effects_logic': ['exact'],
            'fusion_food': ['exact'],
        }

    def filter_name(self, queryset, value):
        if value:
            return queryset.filter(Q(name__icontains=value) | Q(awakens_from__name__icontains=value))
        else:
            return queryset

    def filter_skills__skill_effect__pk(self, queryset, value):
        old_filtering = self.form.cleaned_data.get('effects_logic', False)
        stat_scaling = self.form.cleaned_data.get('skills__scaling_stats__pk', [])

        if old_filtering:
            # Filter if any skill on the monster has the designated fields
            for pk in value:
                queryset = queryset.filter(skills__skill_effect=pk)

            for pk in stat_scaling:
                queryset = queryset.filter(skills__scaling_stats=pk)

            return queryset.distinct()

        else:
            # Filter effects based on effects of each individual skill. This ensures a monster will not show up unless it has
            # the desired effects on the same skill rather than across any skills.

            skills = Skill.objects.all()

            for pk in value:
                skills = skills.filter(skill_effect=pk)

            for pk in stat_scaling:
                skills = skills.filter(scaling_stats=pk)

            return queryset.filter(skills__in=skills).distinct()

    def filter_effects_logic(self, queryset, value):
        # This field is just used to alter the logic of skill effect filter
        return queryset
