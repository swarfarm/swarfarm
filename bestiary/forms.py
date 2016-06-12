from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden, Reset
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton, InlineField, Alert

from bestiary.models import *

import autocomplete_light


class BestiaryQuickSearchForm(forms.Form):
    monster_name = autocomplete_light.ModelChoiceField('BestiaryLinkAutocomplete')

    helper = FormHelper()
    helper.form_action = 'bestiary:home'
    helper.form_method = 'get'
    helper.form_class = 'navbar-form navbar-left hidden-md hidden-sm'
    helper.form_show_labels = False
    helper.layout = Layout(
        FieldWithButtons(
            'monster_name',
            Submit('Go', 'Go'),
        ),
    )


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
