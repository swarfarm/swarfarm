from django import forms
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden, Reset
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton, InlineField, Alert


class ClearProfileFieldMixin(forms.Form):
    clear_profile = forms.BooleanField(label='Clear entire profile on import', required=False, initial=False, help_text='This will clear EVERYTHING in your profile and import fresh data.')


class ImportPCAPForm(ClearProfileFieldMixin, forms.Form):
    pcap = forms.FileField(
        required=True,
    )
    helper = FormHelper()
    helper.form_method = 'POST'

    helper.layout = Layout(
        Alert('Todo: Fill this in', css_class='alert-warning'),
        Field('pcap'),
        Field('clear_profile'),
        FormActions(
            Submit('import', 'Import'),
        ),
    )


class ImportSWParserJSONForm(ClearProfileFieldMixin, forms.Form):
    json_file = forms.FileField(
        required=False,
        label='SWParser JSON File',
    )

    helper = FormHelper()
    helper.form_action = 'sw_parser:import_swparser'
    helper.layout = Layout(
        Alert('Todo: Fill this in', css_class='alert-warning'),
        Field('json_file'),
        Field('clear_profile'),
        FormActions(
            Submit('import', 'Import'),
        ),
    )


class ImportOptimizerForm(ClearProfileFieldMixin, forms.Form):
    json_data = forms.CharField(
        max_length=999999,
        required=True,
        label='Paste Rune Data',
        help_text=mark_safe('Data is exported from the <a href="http://www.graphactory.eu/sw/" target="_blank">Summoners War Rune Database and Optimizer</a>'),
        widget=forms.Textarea(),
    )

    helper = FormHelper()
    helper.layout = Layout(
        Alert('You can only import runes. Importing will create new runes, not update your current runes. Monsters and saved builds from the spreadsheet are ignored.', css_class='alert-warning'),
        Field('json_data'),
        Field('clear_profile'),
        FormActions(
            Submit('import', 'Import'),
        ),
    )

    def clean_json_data(self):
        import json

        data = self.cleaned_data['json_data']

        try:
            data = json.loads(data)
        except:
            raise forms.ValidationError("Error parsing JSON data.")

        return data


class ExportOptimizerForm(forms.Form):
    json_data = forms.CharField(
        max_length=999999,
        label='Exported Rune Data',
        help_text=mark_safe('You can paste this data into the <a href="http://www.graphactory.eu/sw/" target="_blank">Summoners War Rune Database and Optimizer</a>'),
        widget=forms.Textarea(),
    )

    helper = FormHelper()
    helper.form_show_labels = False
    helper.layout = Layout(
        Alert('Importing this data will into the optimizer spreadsheet <strong>OVERWRITE</strong> all runes, monsters, and saved builds currently present. It is advised to back up your existing data first.', css_class='alert-danger'),
        Field('json_data'),
    )
