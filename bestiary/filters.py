import django_filters
from django.db.models import Q

from .models import Monster, SkillEffect, Skill, LeaderSkill, ScalingStat


class MonsterFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_name')
    element = django_filters.MultipleChoiceFilter(choices=Monster.ELEMENT_CHOICES)
    archetype = django_filters.MultipleChoiceFilter(choices=Monster.ARCHETYPE_CHOICES)
    awaken_level = django_filters.MultipleChoiceFilter(choices=Monster.AWAKEN_CHOICES)
    leader_skill__attribute = django_filters.MultipleChoiceFilter(choices=LeaderSkill.ATTRIBUTE_CHOICES)
    leader_skill__area = django_filters.MultipleChoiceFilter(choices=LeaderSkill.AREA_CHOICES)
    skills__scaling_stats__pk = django_filters.ModelMultipleChoiceFilter(queryset=ScalingStat.objects.all(), to_field_name='pk', conjoined=True)
    skills__cooltime = django_filters.CharFilter(method='filter_bypass')
    skills__hits = django_filters.CharFilter(method='filter_bypass')
    effects_logic = django_filters.BooleanFilter(method='filter_bypass')
    skills__skill_effect__pk = django_filters.ModelMultipleChoiceFilter(queryset=SkillEffect.objects.all(), method='filter_skill_effects')
    skills__passive = django_filters.BooleanFilter(method='filter_bypass')
    skills__aoe = django_filters.BooleanFilter(method='filter_bypass')

    class Meta:
        model = Monster
        fields = {
            'name': ['exact'],
            'com2us_id': ['exact'],
            'family_id': ['exact'],
            'element': ['exact'],
            'archetype': ['exact'],
            'base_stars': ['lte', 'gte'],
            'natural_stars': ['lte', 'gte'],
            'obtainable': ['exact'],
            'awaken_level': ['exact'],
            'leader_skill__attribute': ['exact'],
            'leader_skill__area': ['exact'],
            'skills__skill_effect__pk': ['exact'],
            'skills__scaling_stats__pk': ['exact'],
            'skills__passive': ['exact'],
            'skills__aoe': ['exact'],
            'effects_logic': ['exact'],
            'fusion_food': ['exact'],
        }

    def filter_name(self, queryset, name, value):
        if value:
            return queryset.filter(
                Q(name__icontains=value)
                | Q(awakens_from__name__icontains=value)
                | Q(awakens_from__awakens_from__name__icontains=value)
                | Q(awakens_to__name__icontains=value)
            )
        else:
            return queryset

    def filter_skill_effects(self, queryset, name, value):
        old_filtering = self.form.cleaned_data.get('effects_logic', False)
        stat_scaling = self.form.cleaned_data.get('skills__scaling_stats__pk', [])
        passive = self.form.cleaned_data.get('skills__passive', None)
        aoe = self.form.cleaned_data.get('skills__aoe', None)

        try:
            [min_cooltime, max_cooltime] = self.form.cleaned_data['skills__cooltime'].split(',')
            min_cooltime = int(min_cooltime)
            max_cooltime = int(max_cooltime)
        except:
            min_cooltime = None
            max_cooltime = None

        try:
            [min_num_hits, max_num_hits] = self.form.cleaned_data['skills__hits'].split(',')
            min_num_hits = int(min_num_hits)
            max_num_hits = int(max_num_hits)
        except:
            min_num_hits = None
            max_num_hits = None

        if old_filtering:
            # Filter if any skill on the monster has the designated fields
            for effect in value:
                queryset = queryset.filter(skills__skill_effect=effect)

            for pk in stat_scaling:
                queryset = queryset.filter(skills__scaling_stats=pk)

            cooltime_filter = Q()
            
            if max_cooltime is not None and max_cooltime > 0:
                cooltime_filter &= Q(skills__cooltime__lte=max_cooltime)
            
            if min_cooltime is not None and min_cooltime > 0:
                cooltime_filter &= Q(skills__cooltime__gte=min_cooltime)

            if min_cooltime == 0 or max_cooltime == 0:
                cooltime_filter |= Q(skills__cooltime__isnull=True)

            if cooltime_filter:
                queryset = queryset.filter(cooltime_filter)

            if max_num_hits:
                queryset = queryset.filter(skills__hits__lte=max_num_hits)

            if min_num_hits:
                queryset = queryset.filter(skills__hits__gte=min_num_hits)

            if passive is not None:
                queryset = queryset.filter(skills__passive=passive)

            if aoe is not None:
                queryset = queryset.filter(skills__aoe=aoe)

            return queryset.distinct()

        else:
            # Filter effects based on effects of each individual skill. This ensures a monster will not show up unless it has
            # the desired effects on the same skill rather than across any skills.
            skills = Skill.objects.all()
            skills_count = skills.count()

            for effect in value:
                skills = skills.filter(skill_effect=effect)

            for pk in stat_scaling:
                skills = skills.filter(scaling_stats=pk)

            cooltime_filter = Q()

            if max_cooltime is not None and max_cooltime > 0:
                cooltime_filter &= Q(cooltime__lte=max_cooltime)
            
            if min_cooltime is not None and min_cooltime > 0:
                cooltime_filter &= Q(cooltime__gte=min_cooltime)

            if min_cooltime == 0 or max_cooltime == 0:
                cooltime_filter |= Q(cooltime__isnull=True)

            if cooltime_filter:
                skills = skills.filter(cooltime_filter)
            
            hits_filter = Q()

            if max_num_hits:
                hits_filter &= Q(hits__lte=max_num_hits)

            if min_num_hits:
                hits_filter &= Q(hits__gte=min_num_hits)

            if hits_filter:
                skills = skills.filter(hits_filter)

            if passive is not None:
                skills = skills.filter(passive=passive)

            if aoe is not None:
                skills = skills.filter(aoe=aoe)

            # no skill filters
            if skills_count == skills.count():
                return queryset.distinct()

            return queryset.filter(skills__in=skills).distinct()

    def filter_bypass(self, queryset, name, value):
        # This field's logic is applied in filter_skill_effects()
        return queryset
