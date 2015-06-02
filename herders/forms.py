from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator

from .models import MonsterInstance, Summoner

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML
from crispy_forms.bootstrap import FormActions


class RegisterUserForm(forms.Form):
    username = forms.CharField(
        label='Username',
        required=True,
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]+$',
                message='Username must contain only alphanumeric characters and underscore.',
                code='invalid_username'
            ),
        ]
    )

    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput)
    summoner_name = forms.CharField(label='Account Name', required=False)
    is_public = forms.BooleanField(label='Public Profile', required=False)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_action = 'herders:register'
    helper.layout = Layout(
        Field('username', css_class='input-sm'),
        Field('password', css_class='input-sm'),
        Field('summoner_name', css_class='input-sm'),
        Field('is_public'),
        FormActions(Submit('register', 'Register', css_class='btn-lg btn-primary btn-block'))
    )


class EditProfileForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'herders:edit_profile'
        self.helper.layout = Layout(
            Div(
                Field('summoner_name'),
                Field('public'),
                Field('timezone'),
                Field('rep_monster'),
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    HTML("""<a href="{% url 'herders:profile' profile_name=profile_name %}" class="btn btn-link">Cancel</a>"""),
                ),
            ),
        )

    class Meta:
        model = Summoner
        fields = (
            'summoner_name',
            'public',
            'timezone',
            'rep_monster',
        )
        labels = {
            'summoner_name': "Summoner's War Account Name",
            'public': 'Make my collection and in-game account name visible to others',
            'rep_monster': 'Account rep monster',
        }


class EditEssenceStorageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditEssenceStorageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'herders:profile_storage'
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}magic_low.png" class="storage_icon" />"""),
                    Field('storage_magic_low', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}magic_mid.png" class="storage_icon" />"""),
                    Field('storage_magic_mid', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}magic_high.png" class="storage_icon" />"""),
                    Field('storage_magic_high', min=0),
                    css_class='col-md-2 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}fire_low.png" class="storage_icon" />"""),
                    Field('storage_fire_low', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}fire_mid.png" class="storage_icon" />"""),
                    Field('storage_fire_mid', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}fire_high.png" class="storage_icon" />"""),
                    Field('storage_fire_high', min=0),
                    css_class='col-md-2 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}water_low.png" class="storage_icon" />"""),
                    Field('storage_water_low', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}water_mid.png" class="storage_icon" />"""),
                    Field('storage_water_mid', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}water_high.png" class="storage_icon" />"""),
                    Field('storage_water_high', min=0),
                    css_class='col-md-2 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}wind_low.png" class="storage_icon" />"""),
                    Field('storage_wind_low', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}wind_mid.png" class="storage_icon" />"""),
                    Field('storage_wind_mid', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}wind_high.png" class="storage_icon" />"""),
                    Field('storage_wind_high', min=0),
                    css_class='col-md-2 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}light_low.png" class="storage_icon" />"""),
                    Field('storage_light_low', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}light_mid.png" class="storage_icon" />"""),
                    Field('storage_light_mid', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}light_high.png" class="storage_icon" />"""),
                    Field('storage_light_high', min=0),
                    css_class='col-md-2 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}dark_low.png" class="storage_icon" />"""),
                    Field('storage_dark_low', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}dark_mid.png" class="storage_icon" />"""),
                    Field('storage_dark_mid', min=0),
                    css_class='col-md-2 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}dark_high.png" class="storage_icon" />"""),
                    Field('storage_dark_high', min=0),
                    css_class='col-md-2 storage_group',
                ),
                css_class='row',
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    HTML("""<a href="{% url 'herders:profile' profile_name=profile_name %}" class="btn btn-link">Cancel</a>"""),
                ),
            )
        )

    class Meta:
        model = Summoner
        fields = (
            'storage_magic_low',
            'storage_magic_mid',
            'storage_magic_high',
            'storage_fire_low',
            'storage_fire_mid',
            'storage_fire_high',
            'storage_water_low',
            'storage_water_mid',
            'storage_water_high',
            'storage_wind_low',
            'storage_wind_mid',
            'storage_wind_high',
            'storage_light_low',
            'storage_light_mid',
            'storage_light_high',
            'storage_dark_low',
            'storage_dark_mid',
            'storage_dark_high',
        )
        labels = {
            'storage_magic_low': 'Magic Low',
            'storage_magic_mid': 'Magic Mid',
            'storage_magic_high': 'Magic High',
            'storage_fire_low': 'Fire Low',
            'storage_fire_mid': 'Fire Mid',
            'storage_fire_high': 'Fire High',
            'storage_water_low': 'Water Low',
            'storage_water_mid': 'Water Mid',
            'storage_water_high': 'Water High',
            'storage_wind_low': 'Wind Low',
            'storage_wind_mid': 'Wind Mid',
            'storage_wind_high': 'Wind High',
            'storage_light_low': 'Light Low',
            'storage_light_mid': 'Light Mid',
            'storage_light_high': 'Light High',
            'storage_dark_low': 'Dark Low',
            'storage_dark_mid': 'Dark Mid',
            'storage_dark_high': 'Dark High',
        }


class AddMonsterInstanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'herders:add_monster_instance'
        self.helper.layout = Layout(
            Div(
                Field('monster',),
                Field('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                Field('level', value=1),
                Field('fodder', css_class='checkbox'),
                Field('priority',),
                Field('notes'),
                css_class='modal-body',
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    Button('cancel', 'Cancel', css_class='btn btn-link', data_dismiss='modal')
                ),
                css_class='modal-footer',
            )
        )

    class Meta:
        model = MonsterInstance
        fields = ('monster', 'stars', 'level', 'fodder', 'priority', 'notes')


class EditMonsterInstanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        # self.helper.form_action must be set in view
        self.helper.layout = Layout(
            Div(
                Field('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                Field('level'),
                Field('fodder', css_class='checkbox'),
                Field('priority'),
                Field('notes'),
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    HTML("""<a href="{% url 'herders:profile' profile_name=profile_name %}" class="btn btn-link">Cancel</a>"""),
                ),
            )
        )

    class Meta:
        model = MonsterInstance
        exclude = ('owner', 'monster', 'fodder_for')


class AwakenMonsterInstanceForm(forms.Form):
    subtract_materials = forms.BooleanField(
        label='Subtract Materials from stock (Insufficient quantities will be reduced to 0)',
        required=False
    )

    helper = FormHelper()
    helper.form_method = 'post'
    # helper.form_action must be set in view
    helper.layout = Layout(
        Div(
            Field('subtract_materials', css_class='checkbox', checked=''),
        ),
        Div(
            FormActions(
                Submit('awaken', 'Awaken', css_class='btn btn-primary'),
                HTML("""<a href="{% url 'herders:profile' profile_name=profile_name %}" class="btn btn-link">Cancel</a>"""),
            ),
        )
    )
