from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden, Reset
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton, InlineField, Alert

from bestiary.models import Monster

import autocomplete_light


class BestiaryQuickSearchForm(forms.Form):
    monster_name = autocomplete_light.ModelChoiceField('BestiaryLinkAutocomplete')

    helper = FormHelper()
    helper.form_action = 'bestiary:home'
    helper.form_method = 'get'
    helper.form_class = 'navbar-form navbar-left'
    helper.form_show_labels = False
    helper.layout = Layout(
        FieldWithButtons(
            'monster_name',
            Submit('Go', 'Go'),
        ),
    )
