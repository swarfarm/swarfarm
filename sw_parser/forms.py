from django import forms
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, HTML
from crispy_forms.bootstrap import FormActions, Alert

from bestiary.models import Monster
from herders.models import MonsterInstance


class MonsterImportOptionsMixin(forms.Form):
    clear_profile = forms.BooleanField(
        required=False,
        label='Clear entire profile on import. This is recommended for the first Com2US data import. All your notes, priorities, and teams will be lost!',
        help_text=''
    )
    default_priority = forms.ChoiceField(
        label='Default Priority for new monsters',
        choices=MonsterInstance.PRIORITY_CHOICES,
        required=True,
        initial=MonsterInstance.PRIORITY_LOW,
    )
    ignore_fusion = forms.BooleanField(
        required=False,
        label=mark_safe('If monster is locked in-game, do not use for fusion material on SWARFARM. <strong class=text-danger>Requires SWParser 0.96.1 or later.</strong>'),
        initial=True,
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
                HTML("""<h4 class="list-group-item-heading">Options</h4>"""),
                Field('default_priority'),
                Field('ignore_fusion'),
                Field('clear_profile'),
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

    helper.layout = Layout(
        Div(
            Div(
                Field('pcap'),
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
    helper.layout = Layout(
        Div(
            Div(
                Field('json_file'),
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
        help_text=mark_safe('Data is exported from the <a href="http://swrunes.all.my/" target="_blank">Summoners War Rune Database and Optimizer</a>'),
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
        help_text=mark_safe('You can paste this data into the <a href="http://swrunes.all.my/" target="_blank">Summoners War Rune Database and Optimizer</a>'),
        widget=forms.Textarea(),
    )

    helper = FormHelper()
    helper.form_show_labels = False
    helper.layout = Layout(
        Alert('Importing this data will into the optimizer spreadsheet <strong>OVERWRITE</strong> all runes, monsters, and saved builds currently present. It is advised to back up your existing data first.', css_class='alert-danger'),
        Field('json_data'),
    )


class ApplyImportForm(forms.Form):
    missing_choices = (
        (1, 'Delete missing'),
        (0, 'Do not delete')
    )

    missing_monster_action = forms.TypedChoiceField(
        label='Action for missing monsters: ',
        initial=1,
        required=True,
        choices=missing_choices,
        widget=forms.RadioSelect,
        coerce=int,
    )
    missing_rune_action = forms.TypedChoiceField(
        label='Action for missing runes: ',
        initial=1,
        required=True,
        choices=missing_choices,
        widget=forms.RadioSelect,
        coerce=int,
    )

    helper = FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-2'
    helper.field_class = 'col-md-8'
    helper.layout = Layout(
        Field('missing_monster_action'),
        Field('missing_rune_action'),
        FormActions(
            Submit('finalize', 'Finalize Import', css_class='btn-success'),
        ),
    )