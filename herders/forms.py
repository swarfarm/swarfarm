from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm

from .models import MonsterInstance, Summoner, TeamGroup, Team

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden
from crispy_forms.bootstrap import FormActions

from captcha.fields import ReCaptchaField

import autocomplete_light

# User stuff
class CrispyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CrispyAuthenticationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'login'
        self.helper.layout = Layout(
            Field('username'),
            Field('password'),
            Hidden('next', value='{{ next }}'),
            FormActions(Submit('login', 'Log In', css_class='btn-lg btn-primary btn-block')),
        )

class CrispyPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(CrispyPasswordChangeForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'password_change'
        self.helper.layout = Layout(
            Field('old_password'),
            Field('new_password1'),
            Field('new_password2'),
            FormActions(Submit('submit', 'Submit', css_class='btn-lg btn-primary btn-block')),
        )

class CrispyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CrispyPasswordResetForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'password_reset'
        self.helper.layout = Layout(
            Field('email'),
            FormActions(Submit('submit', 'Submit', css_class='btn-lg btn-primary btn-block')),
        )

class CrispySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CrispySetPasswordForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('new_password1'),
            Field('new_password2'),
            FormActions(Submit('submit', 'Submit', css_class='btn-lg btn-primary btn-block')),
        )

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

    email = forms.EmailField(required=True, help_text='Your email address will only be used for password resets and account expiration notices.')
    password = forms.CharField(label="Password", required=True, widget=forms.PasswordInput)
    summoner_name = forms.CharField(label="Summoner's War Account Name", required=False, help_text='Not required. Visible to others if you make your SWARFARM account public.')
    is_public = forms.BooleanField(label='Make my SWARFARM account visible to others', required=False)
    captcha = ReCaptchaField()

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_action = 'herders:register'
    helper.layout = Layout(
        Field('username', css_class='input-sm'),
        Field('password', css_class='input-sm'),
        Field('email', css_class='input-sm'),
        Field('summoner_name', css_class='input-sm'),
        Field('is_public'),
        Field('captcha'),
        FormActions(Submit('register', 'Register', css_class='btn-lg btn-primary btn-block'))
    )

class EditUserForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('email'),
            )
        )

    class Meta:
        model = User
        fields = (
            'email',
        )

class EditSummonerForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditSummonerForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('summoner_name'),
                Field('public'),
                Field('timezone'),
            ),
        )

    class Meta:
        model = Summoner
        fields = (
            'summoner_name',
            'public',
            'timezone',
        )
        labels = {
            'summoner_name': "Summoner's War Account Name",
            'public': 'Make my SWARFARM account visible to others',
        }


# SWARFARM forms
class EditEssenceStorageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditEssenceStorageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_show_labels = True
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}magic_low.png" class="storage_icon" />"""),
                    Field('storage_magic_low', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}magic_mid.png" class="storage_icon" />"""),
                    Field('storage_magic_mid', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}magic_high.png" class="storage_icon" />"""),
                    Field('storage_magic_high', min=0),
                    css_class='col-md-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}fire_low.png" class="storage_icon" />"""),
                    Field('storage_fire_low', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}fire_mid.png" class="storage_icon" />"""),
                    Field('storage_fire_mid', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}fire_high.png" class="storage_icon" />"""),
                    Field('storage_fire_high', min=0),
                    css_class='col-md-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}water_low.png" class="storage_icon" />"""),
                    Field('storage_water_low', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}water_mid.png" class="storage_icon" />"""),
                    Field('storage_water_mid', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}water_high.png" class="storage_icon" />"""),
                    Field('storage_water_high', min=0),
                    css_class='col-md-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}wind_low.png" class="storage_icon" />"""),
                    Field('storage_wind_low', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}wind_mid.png" class="storage_icon" />"""),
                    Field('storage_wind_mid', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}wind_high.png" class="storage_icon" />"""),
                    Field('storage_wind_high', min=0),
                    css_class='col-md-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}light_low.png" class="storage_icon" />"""),
                    Field('storage_light_low', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}light_mid.png" class="storage_icon" />"""),
                    Field('storage_light_mid', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}light_high.png" class="storage_icon" />"""),
                    Field('storage_light_high', min=0),
                    css_class='col-md-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}dark_low.png" class="storage_icon" />"""),
                    Field('storage_dark_low', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}dark_mid.png" class="storage_icon" />"""),
                    Field('storage_dark_mid', min=0),
                    css_class='col-md-1 storage_group',
                ),
                Div(
                    HTML("""<img src="{{ essence_url_prefix }}dark_high.png" class="storage_icon" />"""),
                    Field('storage_dark_high', min=0),
                    css_class='col-md-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    HTML("""<a href="{{ return_path }}" class="btn btn-link">Cancel</a>"""),
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

class AddMonsterInstanceForm(autocomplete_light.ModelForm):
    monster = autocomplete_light.ModelChoiceField('MonsterAutocomplete')

    def __init__(self, *args, **kwargs):
        super(AddMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Field('monster'),
                Field('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                Field('level', value=1, min=1, max=40),
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
        self.helper.layout = Layout(
            Div(
                Field('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                Field('level', min=1, max=40),
                Field('fodder', css_class='checkbox'),
                Field('in_storage', css_class='checkbox'),
                Field('priority'),
                Field('notes'),
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    HTML("""<a href="{{ return_path }}" class="btn btn-link">Cancel</a>"""),
                ),
            )
        )

    class Meta:
        model = MonsterInstance
        exclude = ('owner', 'monster', 'fodder_for')

class PowerUpMonsterInstanceForm(forms.Form):
    monster = autocomplete_light.ModelChoiceField('MonsterInstanceAutocomplete')
    monster.label = 'Material Monster'
    monster.required = False

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_tag = False
    helper.layout = Layout(
        Field('monster'),
    )

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
                HTML("""<a href="{{ return_path }}" class="btn btn-link">Cancel</a>"""),
            ),
        )
    )

class AddTeamGroupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddTeamGroupForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        # helper.form_action must be set in view
        self.helper.layout = Layout(
            Div(
                Field('name'),
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
        model = TeamGroup
        exclude = ('id', 'owner')

class DeleteTeamGroupForm(forms.Form):
    reassign_group = forms.ModelChoiceField(
        queryset=TeamGroup.objects.all(),
        required=True,
        label="Reassign teams in this group to"
    )

    helper = FormHelper()
    helper.form_method = 'post'
    # helper.form_action must be set in view
    helper.layout = Layout(
        Field('reassign_group', css_class='input-sm'),
        FormActions(
            Submit('apply', 'Apply', css_class='btn btn-primary'),
            Submit('delete', 'Delete all teams', css_class='btn btn-danger'),
        )
    )

class EditTeamForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditTeamForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'EditTeamForm'
        self.helper.layout = Layout(
            Div(
                Field('group'),
                Field('name'),
                Field('favorite'),
            ),
            Field('description'),
            Field('leader'),
            Field('roster'),
            FormActions(
                Submit('save', 'Save', css_class='btn btn-primary'),
            ),
        )

    class Meta:
        model = Team
        exclude = ('id',)
        widgets = {
            'roster': autocomplete_light.MultipleChoiceWidget('MonsterInstanceAutocomplete'),
            'leader': autocomplete_light.ChoiceWidget('MonsterInstanceAutocomplete'),
        }
        help_texts = {
            'description': 'Markdown syntax enabled'
        }

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check that leader is not also in the roster
        leader = self.cleaned_data.get('leader')
        roster = self.cleaned_data.get('roster')

        print leader
        print roster

        if leader in roster:
            raise ValidationError(
                'Leader cannot be included in the roster as well',
                code='leader_in_roster'
            )

        super(EditTeamForm, self).clean()
