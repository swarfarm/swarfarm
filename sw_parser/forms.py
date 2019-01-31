from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from crispy_forms.bootstrap import FormActions


class FilterLogTimeRangeForm(forms.Form):
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()

    helper = FormHelper()
    helper.layout = Layout(
        Field('start_time'),
        Field('end_time'),
        FormActions(
            Submit('apply', 'Apply'),
        )
    )
