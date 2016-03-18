from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden, Reset
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton, InlineField, Alert

from bestiary.models import Monster

import autocomplete_light


class BestiaryQuickSearchForm(forms.Form):
    monster = autocomplete_light.ModelChoiceField('BestiaryLinkAutocomplete')

    helper = FormHelper()
    helper.form_class = 'navbar-form navbar-left'
    helper.form_show_labels = False
    helper.layout = Layout(
        FieldWithButtons(
            'monster',
            HTML("""
            <a href="{% url 'bestiary:home' %}" class="btn btn-default {% if view == 'bestiary' %}active{% endif %}">
                <span class="fa fa-book hidden-sm"></span>
                Bestiary
            </a>"""),
        ),
    )