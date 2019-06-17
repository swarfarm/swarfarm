import django_filters
from django.db.models import Q

from .models import Monster, SkillEffect, Skill, LeaderSkill, ScalingStat


class MonsterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')
    element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    archetype = django_filters.MultipleChoiceFilter(choices=Monster.TYPE_CHOICES)
    awaken_level = django_filters.MultipleChoiceFilter(choices=Monster.AWAKEN_CHOICES)
    leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=LeaderSkill.ATTRIBUTE_CHOICES)
    leader_skill__area = django_filters.MultipleChoiceFilter(choices=LeaderSkill.AREA_CHOICES)
    skills__scaling_stats__pk = django_filters.ModelMultipleChoiceFilter(queryset=ScalingStat.objects.all(), to_field_name='pk', conjoined=True)
    skills__cooltime = django_filters.CharFilter(method='filter_skills_cooltime')
    effects_logic = django_filters.BooleanFilter(method='filter_effects_logic')
    skills__skill_effect__pk = django_filters.ModelMultipleChoiceFilter(queryset=SkillEffect.objects.all(), method='filter_skill_effects')

    class Meta:
        model = Monster
        fields = {
            'name': ['exact'],
            'com2us_id': ['exact'],
            'family_id': ['exact'],
            'element': ['exact'],
            'archetype': ['exact'],
            'base_stars': ['lte', 'gte'],
            'obtainable': ['exact'],
            'awaken_level': ['exact'],
            'leader_skill__attribute': ['exact'],
            'leader_skill__area': ['exact'],
            'skills__skill_effect__pk': ['exact'],
            'skills__scaling_stats__pk': ['exact'],
            'skills__cooltime': ['lte', 'gte'],
            'skills__hits': ['lte', 'gte'],
            'effects_logic': ['exact'],
            'fusion_food': ['exact'],
        }

    def filter_name(self, queryset, name, value):
        if value:
            return queryset.filter(Q(name__icontains=value) | Q(awakens_from__name__icontains=value) | Q(awakens_to__name__icontains=value))
        else:
            return queryset

    def filter_skill_effects(self, queryset, name, value):
        old_filtering = self.form.cleaned_data.get('effects_logic', False)
        stat_scaling = self.form.cleaned_data.get('skills__scaling_stats__pk', [])
        cooltimes = self.form.cleaned_data.get('skills__cooltime', '')
        max_num_hits = self.form.cleaned_data.get('skills__hits__lte', 99)
        min_num_hits = self.form.cleaned_data.get('skills__hits__gte', 0)

        try:
            cooltimes = cooltimes.split(',')
            min_cooltime = int(cooltimes[0])
            max_cooltime = int(cooltimes[1])
        except:
            min_cooltime = 0
            max_cooltime = 999

        if old_filtering:
            # Filter if any skill on the monster has the designated fields
            for effect in value:
                queryset = queryset.filter(skills__skill_effect=effect)

            for pk in stat_scaling:
                queryset = queryset.filter(skills__scaling_stats=pk)

            cooltime_filter = Q(skills__cooltime__gte=min_cooltime) & Q(skills__cooltime__lte=max_cooltime)
            if min_cooltime == 0 or max_cooltime == 0:
                cooltime_filter = Q(skills__cooltime__isnull=True) | cooltime_filter

            queryset = queryset.filter(cooltime_filter, skills__hits__lte=max_num_hits, skills__hits__gte=min_num_hits)

            return queryset.distinct()

        else:
            # Filter effects based on effects of each individual skill. This ensures a monster will not show up unless it has
            # the desired effects on the same skill rather than across any skills.
            skills = Skill.objects.all()

            for effect in value:
                skills = skills.filter(skill_effect=effect)

            for pk in stat_scaling:
                skills = skills.filter(scaling_stats=pk)

            cooltime_filter = Q(cooltime__gte=min_cooltime) & Q(cooltime__lte=max_cooltime)
            if min_cooltime == 0 or max_cooltime == 0:
                cooltime_filter = Q(cooltime__isnull=True) | cooltime_filter

            skills = skills.filter(cooltime_filter, hits__lte=max_num_hits, hits__gte=min_num_hits)

            return queryset.filter(skills__in=skills).distinct()

    def filter_effects_logic(self, queryset, name, value):
        # This field is just used to alter the logic of skill effect filter
        return queryset

    def filter_skills_cooltime(self, queryset, name, value):
        # This field is handled in filter_skill_effects()
        return queryset

    def filter_skills_slot(self, queryset, name, value):
        # This field is handled in filter_skill_effects()
        return queryset

    def filter_skills_hits(self, queryset, name, value):
        # This field is handled in filter_skill_effects()
        return queryset
