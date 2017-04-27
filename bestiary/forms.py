from itertools import chain

from django import forms
from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, Fieldset
from crispy_forms.bootstrap import FormActions

from bestiary.models import *

STATIC_URL_PREFIX = static('herders/images/')


# Bestiary forms
class BestiaryQuickSearchForm(forms.Form):
    name = forms.MultipleChoiceField()

    helper = FormHelper()
    helper.form_action = 'bestiary:home'
    helper.form_method = 'post'
    helper.form_class = 'navbar-form navbar-left hidden-sm'
    helper.form_show_labels = False
    helper.include_media = False
    helper.layout = Layout(
        Div(
            Field(
                'name',
                id='bestiary_quick_name',
                css_class='select2',
                data_placeholder='Quick Search...',
                data_ajax__url=reverse_lazy('bestiary-monster-autocomplete'),
                data_selection_template="monsterSelect2Template",
                data_result_template="monsterSelect2Template",
            ),
            css_class='input-group'
        ),
    )


class FilterMonsterForm(forms.Form):
    name = forms.CharField(
        label='Monster Name',
        max_length=100,
        required=False,
    )
    base_stars = forms.CharField(
        label='Base Stars',
        required=False,
    )
    element = forms.MultipleChoiceField(
        label='Element',
        choices=Monster.ELEMENT_CHOICES,
        required=False,
    )
    archetype = forms.MultipleChoiceField(
        label='Archetype',
        choices=Monster.TYPE_CHOICES,
        required=False,
    )
    is_awakened = forms.NullBooleanField(label='Awakened', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    fusion_food = forms.NullBooleanField(label='Fusion Food', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    leader_skill__attribute = forms.MultipleChoiceField(
        label='Leader Skill Stat',
        choices=LeaderSkill.ATTRIBUTE_CHOICES,
        required=False,
    )
    leader_skill__area = forms.MultipleChoiceField(
        label='Leader Skill Area',
        choices=LeaderSkill.AREA_CHOICES,
        required=False,
    )
    skills__scaling_stats__pk = forms.ModelMultipleChoiceField(
        label='Scales With',
        queryset=ScalingStat.objects.all(),
        required=False,
    )
    buffs = forms.ModelMultipleChoiceField(
        label='Buffs',
        queryset=Effect.objects.filter(is_buff=True).exclude(icon_filename=''),
        required=False,
    )
    debuffs = forms.ModelMultipleChoiceField(
        label='Debuffs',
        queryset=Effect.objects.filter(is_buff=False).exclude(icon_filename=''),
        required=False,
    )
    other_effects = forms.ModelMultipleChoiceField(
        label='Other Effects',
        queryset=Effect.other_effect_choices.all(),
        required=False,
    )
    effects_logic = forms.BooleanField(
        label=mark_safe('<span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" title="Whether all effect filters must be on ONE individual skill or can be spread across ANY skill in a monster\'s skill set."></span>'),
        required=False,
        initial=True,
    )
    page = forms.IntegerField(required=False)
    sort = forms.CharField(required=False)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'FilterBestiaryForm'
    helper.layout = Layout(
        Div(
            Fieldset(
                'General',
                Div(
                    Field('name', wrapper_class='form-group-sm form-group-condensed col-md-8'),
                    Field(
                        'base_stars',
                        data_provide='slider',
                        data_slider_min='1',
                        data_slider_max='6',
                        data_slider_value='[1, 6]',
                        data_slider_step='1',
                        data_slider_ticks='[1, 6]',
                        data_slider_ticks_labels='["1", "6"]',
                        wrapper_class='form-group-sm form-group-condensed col-md-4'
                    ),
                    Field('is_awakened', wrapper_class='form-group-sm form-group-condensed col-md-6'),
                    Field('fusion_food', wrapper_class='form-group-sm form-group-condensed col-md-6'),
                    Field('element', css_class='select2-element', wrapper_class='form-group-sm form-group-condensed col-md-6'),
                    Field('archetype', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-6'),
                    css_class='row',
                ),
                css_class='col-md-4'
            ),
            Fieldset(
                'Skills',
                Div(
                    Field('buffs', css_class='select2-effect', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field('debuffs', css_class='select2-effect', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field('other_effects', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field('skills__scaling_stats__pk', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field('effects_logic', data_toggle='toggle', data_on='Any Skill', data_onstyle='primary', data_off='One Skill', data_offstyle='primary', data_width='125px', wrapper_class='form-group-sm form-group-condensed col-lg-12'),
                    css_class='row'
                ),
                css_class='col-md-4'
            ),
            Fieldset(
                'Leader Skill',
                Field('leader_skill__attribute', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('leader_skill__area', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                css_class='col-md-4'
            ),
            css_class='row'
        ),
        Div(
            Div(
                Submit('apply', 'Apply', css_class='btn-success'),
                css_class='btn-group'
            ),
            Div(
                Button('resetBtn', 'Reset Filters', css_class='btn-danger reset'),
                css_class='btn-group'
            ),
            css_class='btn-group btn-group-justified'
        ),
        Field('page', value=1, type='hidden'),
        Field('sort', value='', type='hidden'),
    )

    def clean(self):
        super(FilterMonsterForm, self).clean()

        # Coalesce the effect fields into a single one that the filter can understand
        selected_buff_effects = self.cleaned_data.get('buffs')
        selected_debuff_effects = self.cleaned_data.get('debuffs')
        selected_other_effects = self.cleaned_data.get('other_effects')
        self.cleaned_data['skills__skill_effect__pk'] = chain(selected_buff_effects, selected_debuff_effects, selected_other_effects)

        # Split the slider ranges into two min/max fields for the filters
        try:
            [min_stars, max_stars] = self.cleaned_data['base_stars'].split(',')
        except:
            min_stars = 1
            max_stars = 6

        self.cleaned_data['base_stars__gte'] = int(min_stars)
        self.cleaned_data['base_stars__lte'] = int(max_stars)


# Superuser edit forms
class SkillForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SkillForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'bestiary:edit_skill'
        self.helper.form_class = 'ajax-form'
        self.helper.layout = Layout(
            Field('name'),
            Field('com2us_id'),
            Field('description'),
            Field('slot'),
            Field('skill_effect'),
            Field('cooltime'),
            Field('hits'),
            Field('aoe'),
            Field('passive'),
            Field('max_level'),
            Field('level_progress_description'),
            Field('icon_filename'),
            Field('atk_multiplier'),
            FormActions(
                Submit('submit', 'Submit')
            )
        )

    class Meta:
        model = Skill
        exclude = ('pk', 'effect', 'scales_with')
