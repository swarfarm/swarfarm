from itertools import chain

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, Fieldset
from dal import autocomplete
from django import forms
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from .fields import AdvancedSelectMultiple
from .models import Monster, LeaderSkill, ScalingStat, SkillEffect
from .widgets import EffectSelectMultipleWidget, ElementSelectMultipleWidget

STATIC_URL_PREFIX = static('herders/images/')


# Bestiary forms
class BestiaryQuickSearchForm(forms.Form):
    name = forms.ModelChoiceField(
        queryset=Monster.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='bestiary-quicksearch-autocomplete',
            attrs={
                'data-ajax-delay': 250,
                'data-html': True,
                'data-placeholder': 'Quick search',
            }
        ),
    )

    helper = FormHelper()
    helper.form_action = 'bestiary:home'
    helper.form_method = 'post'
    helper.form_class = 'navbar-form navbar-left hidden-sm'
    helper.form_id = 'bestiary_quick_search'
    helper.form_show_labels = False
    helper.include_media = False
    helper.layout = Layout(
        Div(
            Field(
                'name',
            ),
            css_class='input-group navbar-autocomplete'
        ),
    )


def effect_choices(effects):
    choices = []

    for buff in effects.order_by('name'):
        # Select2 template splits the string at ; to get an image and name
        choices.append((buff.pk, STATIC_URL_PREFIX + 'buffs/' + buff.icon_filename + ';' + buff.name))

    return choices


class FilterMonsterForm(forms.Form):
    name = forms.CharField(
        label='Monster Name',
        max_length=100,
        required=False,
    )
    natural_stars = forms.CharField(
        label='Natural Stars',
        required=False,
    )
    element = forms.MultipleChoiceField(
        label='Element',
        choices=Monster.ELEMENT_CHOICES,
        required=False,
        widget=ElementSelectMultipleWidget,
    )
    archetype = forms.MultipleChoiceField(
        label='Archetype',
        choices=Monster.ARCHETYPE_CHOICES,
        required=False,
    )
    awaken_level = forms.MultipleChoiceField(
        label='Awakening Level',
        choices=Monster.AWAKEN_CHOICES[:3],  # Excluding 'incomplete'
        required=False,
    )
    fusion_food = forms.NullBooleanField(
        label='Fusion Food',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
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
    skills__cooltime = forms.CharField(
        label="Cooldown",
        required=False,
    )
    skills__hits = forms.CharField(
        label="Number of Hits",
        required=False,
    )
    skills__passive = forms.NullBooleanField(
        label="Passive",
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    skills__aoe = forms.NullBooleanField(
        label="AOE",
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    buffs = AdvancedSelectMultiple(
        label='Buffs',
        queryset=SkillEffect.objects.filter(type=SkillEffect.TYPE_BUFF),
        required=False,
        widget=EffectSelectMultipleWidget
    )
    debuffs = AdvancedSelectMultiple(
        label='Debuffs',
        queryset=SkillEffect.objects.filter(type=SkillEffect.TYPE_DEBUFF),
        required=False,
        widget=EffectSelectMultipleWidget,
    )
    other_effects = forms.ModelMultipleChoiceField(
        label='Other Effects',
        queryset=SkillEffect.objects.filter(type=SkillEffect.TYPE_NEUTRAL),
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
    helper.form_method = 'get'
    helper.form_id = 'FilterBestiaryForm'
    helper.layout = Layout(
        Div(
            Fieldset(
                'General',
                Div(
                    Field('name', wrapper_class='form-group-sm form-group-condensed col-md-8'),
                    Field(
                        'natural_stars',
                        data_provide='slider',
                        data_slider_min='1',
                        data_slider_max='6',
                        data_slider_value='[1, 6]',
                        data_slider_step='1',
                        data_slider_ticks='[1, 6]',
                        data_slider_ticks_labels='["1", "6"]',
                        wrapper_class='form-group-sm form-group-condensed col-md-4'
                    ),
                    Field(
                        'awaken_level',
                        css_class='select2',
                        wrapper_class='form-group-sm form-group-condensed col-md-6'
                    ),
                    Field('fusion_food', wrapper_class='form-group-sm form-group-condensed col-md-6'),
                    Field(
                        'element',
                        css_class='select2',
                        data_result_template='iconSelect2Template',
                        data_selection_template='iconSelect2Template',
                        wrapper_class='form-group-sm form-group-condensed col-md-6'
                    ),
                    Field('archetype', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-6'),
                    css_class='row',
                ),
                css_class='col-md-4'
            ),
            Fieldset(
                'Skills',
                Div(
                    Field(
                        'buffs',
                        css_class='select2',
                        data_result_template='iconSelect2Template',
                        data_selection_template='iconSelect2Template',
                        wrapper_class='form-group-sm form-group-condensed col-lg-6'
                    ),
                    Field(
                        'debuffs',
                        css_class='select2',
                        data_result_template='iconSelect2Template',
                        data_selection_template='iconSelect2Template',
                        wrapper_class='form-group-sm form-group-condensed col-lg-6'
                    ),
                    Field('other_effects', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field('skills__scaling_stats__pk', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field('skills__passive', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field('skills__aoe', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                    Field(
                        'skills__cooltime',
                        data_provide='slider',
                        data_slider_min='0',
                        data_slider_max='13',
                        data_slider_value='[0, 13]',
                        data_slider_step='1',
                        data_slider_ticks='[0, 13]',
                        data_slider_ticks_labels='["0", "13"]',
                        wrapper_class='col-lg-6'
                    ),
                    Field(
                        'skills__hits',
                        data_provide='slider',
                        data_slider_min='0',
                        data_slider_max='7',
                        data_slider_value='[0, 7]',
                        data_slider_step='1',
                        data_slider_ticks='[0, 7]',
                        data_slider_ticks_labels='["0", "7"]',
                        wrapper_class='form-group-sm form-group-condensed col-lg-6'
                    ),
                    Field(
                        'effects_logic',
                        data_toggle='toggle',
                        data_on='Any Skill',
                        data_onstyle='primary',
                        data_off='One Skill',
                        data_offstyle='primary',
                        data_width='125px',
                        wrapper_class='form-group-sm form-group-condensed col-lg-12'
                    ),
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
        self.cleaned_data['skills__effect__pk'] = chain(selected_buff_effects, selected_debuff_effects, selected_other_effects)

        # Split the slider ranges into two min/max fields for the automatic filters
        try:
            [min_stars, max_stars] = self.cleaned_data['natural_stars'].split(',')
            self.cleaned_data['natural_stars__gte'] = int(min_stars)
            self.cleaned_data['natural_stars__lte'] = int(max_stars)
        except:
            self.cleaned_data['natural_stars__gte'] = None
            self.cleaned_data['natural_stars__lte'] = None
