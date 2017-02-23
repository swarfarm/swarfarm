from django import forms
from django.utils.safestring import mark_safe
from django.db.models.fields import BLANK_CHOICE_DASH

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, HTML
from crispy_forms.bootstrap import FormActions, Alert

from bestiary.models import Monster
from herders.models import MonsterInstance


class MonsterImportOptionsMixin(forms.Form):
    missing_choices = (
        (1, 'Delete missing'),
        (0, 'Do not delete')
    )

    missing_monster_action = forms.TypedChoiceField(
        label='Action for monsters not in import data',
        initial=1,
        required=True,
        choices=missing_choices,
        widget=forms.RadioSelect,
        coerce=int,
    )
    missing_rune_action = forms.TypedChoiceField(
        label='Action for runes not in import data',
        initial=1,
        required=True,
        choices=missing_choices,
        widget=forms.RadioSelect,
        coerce=int,
    )
    clear_profile = forms.BooleanField(
        required=False,
        label='Clear entire profile on import. This is recommended for the first Com2US data import. All your notes, priorities, and teams will be lost!',
        help_text=''
    )
    default_priority = forms.ChoiceField(
        label='Default Priority for new monsters',
        choices=BLANK_CHOICE_DASH + MonsterInstance.PRIORITY_CHOICES,
        required=False,
    )
    minimum_stars = forms.ChoiceField(
        label='Minimum stars',
        choices=Monster.STAR_CHOICES,
        required=True,
        widget=forms.RadioSelect,
        initial=1,
    )
    ignore_silver = forms.BooleanField(
        required=False,
        label="Ignore silver star monsters that can't be awakened"
    )
    ignore_material = forms.BooleanField(
        required=False,
        label="Ignore material type monsters (Rainbowmon, Angelmon, and Devilmon)"
    )
    except_with_runes = forms.BooleanField(
        required=False,
        label='Import anyway if monster has equipped runes',
        initial=True,
    )
    except_light_and_dark = forms.BooleanField(
        required=False,
        label='Import anyway if monster is Light or Dark',
        initial=True,
    )
    lock_monsters = forms.BooleanField(
        required=False,
        label=mark_safe('<span class="glyphicon glyphicon-lock"></span> Copy locked status of monsters from in-game'),
        help_text='Locking on SWARFARM means a monster will not be used as fusion ingredients or skill-ups.',
        initial=True,
    )


class MonsterImportOptionsLayout(Layout):
    def __init__(self):
        super(MonsterImportOptionsLayout, self).__init__(
            Div(
                HTML("""<h4 class="list-group-item-heading">Monster Filters</h4>"""),
                Alert(content="Note: If a monster is filtered out, it's equipped runes will not be imported either!", css_class='alert-warning'),
                Field('minimum_stars', template='crispy/button_radio_select.html'),
                Field('ignore_silver'),
                Field('ignore_material'),
                Field('except_with_runes'),
                Field('except_light_and_dark'),
                css_class='list-group-item',
            ),
            Div(
                HTML("""<h4 class="list-group-item-heading">Import Options</h4>"""),
                Field('default_priority'),
                Field('lock_monsters'),
                Field('missing_monster_action'),
                Field('missing_rune_action'),
                Div(
                    Field('clear_profile'),
                    css_class='alert alert-danger'
                ),
                css_class='list-group-item',
            ),
        )


class ImportPCAPForm(MonsterImportOptionsMixin, forms.Form):
    pcap = forms.FileField(
        required=True,
        label='PCAP File',
    )
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.form_class = 'import-form'

    helper.layout = Layout(
        Div(
            Div(
                Field('pcap', template='crispy/file_upload.html'),
                css_class='list-group-item',
            ),
            MonsterImportOptionsLayout(),
            Div(
                FormActions(
                    Submit('import', 'Import'),
                ),
                css_class='list-group-item',
            ),
            css_class='list-group',
        )
    )


class ImportSWParserJSONForm(MonsterImportOptionsMixin, forms.Form):
    json_file = forms.FileField(
        required=True,
        label='SWParser JSON File',
    )

    helper = FormHelper()
    helper.form_action = 'sw_parser:import_swparser'
    helper.form_class = 'import-form'
    helper.layout = Layout(
        Div(
            Div(
                Field('json_file', template='crispy/file_upload.html'),
                css_class='list-group-item',
            ),
            MonsterImportOptionsLayout(),
            Div(
                FormActions(
                    Submit('import', 'Import'),
                ),
                css_class='list-group-item',
            ),
            css_class='list-group',
        )
    )


class ImportOptimizerForm(forms.Form):
    json_data = forms.CharField(
        max_length=999999,
        required=True,
        label='Paste Rune Data',
        widget=forms.Textarea(attrs={'placeholder': 'Paste data here'}),
    )

    helper = FormHelper()
    helper.form_show_labels = False
    helper.layout = Layout(
        Field('json_data'),
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
        max_length=9999999,
        label='Exported Rune Data',
        widget=forms.Textarea(),
    )

    helper = FormHelper()
    helper.form_show_labels = False
    helper.layout = Layout(
        Field('json_data'),
    )


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
