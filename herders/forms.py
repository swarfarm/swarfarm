from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.templatetags.static import static

from .models import Monster, MonsterInstance, Summoner, TeamGroup, Team

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton, InlineField, InlineCheckboxes

from captcha.fields import ReCaptchaField

import autocomplete_light


STATIC_URL_PREFIX = static('herders/images/')


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


class CrispyChangeUsernameForm(forms.Form):
    username = forms.CharField(
        label='New Username',
        required=True,
        help_text='This will change the username used to log in and the URL used to access your profile.',
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9_]+$',
                message='Username must contain only alphanumeric characters and underscore.',
                code='invalid_username'
            ),
        ]
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_action = 'username_change'
    helper.layout = Layout(
        Field('username', css_class='input-sm'),
        FormActions(Submit('change', 'Change', css_class='btn-lg btn-primary btn-block'))
    )


class RegisterUserForm(forms.Form):
    username = forms.CharField(
        label='Username',
        required=True,
        help_text='Used to link to your profile to others: http://swarfarm.com/profile/&lt;username&gt;/view',
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


class DeleteProfileForm(forms.Form):
    confirmbox = forms.BooleanField(label="I seriously do want to delete my account and all associated data", required=True)
    passcode = forms.CharField(
        label='Acknowledgement:',
        required=True,
        help_text='Enter the following text: I acknowledge everything will be permanently deleted',
        validators=[
            RegexValidator(
                regex='^I acknowledge everything will be permanently deleted$',
                message="You didn't enter the correct text.",
                code='invalid_acknowledgement'
            )
        ]
    )
    captcha = ReCaptchaField()

    helper = FormHelper()
    helper.form_method = 'post'
    helper.layout = Layout(
        Div(
            Field('confirmbox', css_class='checkbox'),
            Field('passcode', css_class='input-sm'),
            Field('captcha'),
            FormActions(
                Submit('delete', 'Delete', css_class='btn-lg btn-danger btn-block'),
            ),
            css_class='col-md-6 col-md-offset-3',
        ),
    )


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
                    PrependedText('storage_magic_low', '<img src="' + STATIC_URL_PREFIX + 'essences/magic_low.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_magic_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/magic_mid.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_magic_high', '<img src="' + STATIC_URL_PREFIX + 'essences/magic_high.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_fire_low', '<img src="' + STATIC_URL_PREFIX + 'essences/fire_low.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_fire_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/fire_mid.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_fire_high', '<img src="' + STATIC_URL_PREFIX + 'essences/fire_high.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_water_low', '<img src="' + STATIC_URL_PREFIX + 'essences/water_low.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_water_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/water_mid.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_water_high', '<img src="' + STATIC_URL_PREFIX + 'essences/water_high.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_wind_low', '<img src="' + STATIC_URL_PREFIX + 'essences/wind_low.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_wind_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/wind_mid.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_wind_high', '<img src="' + STATIC_URL_PREFIX + 'essences/wind_high.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_light_low', '<img src="' + STATIC_URL_PREFIX + 'essences/light_low.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_light_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/light_mid.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_light_high', '<img src="' + STATIC_URL_PREFIX + 'essences/light_high.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_dark_low', '<img src="' + STATIC_URL_PREFIX + 'essences/dark_low.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_dark_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/dark_mid.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                Div(
                    PrependedText('storage_dark_high', '<img src="' + STATIC_URL_PREFIX + 'essences/dark_high.png" />', min=0),
                    css_class='col-lg-1 storage_group',
                ),
                css_class='row',
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
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
                Field(
                    'monster',
                    data_toggle='popover',
                    data_trigger='focus',
                    data_container='body',
                    title='Autocomplete Tips',
                    data_content="Enter the monster's awakened or unawakened name (either will work). To further narrow results, type the element too. Example: \"Raksha water\" will list water Rakshasa and Su",
                    data_stars_field=self['stars'].auto_id,
                    data_set_stars='',
                ),
                Field('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                FieldWithButtons(
                    Field('level', value=1, min=1, max=40),
                    StrictButton("Max", name="Set_Max_Level", data_stars_field=self['stars'].auto_id, data_level_field=self['level'].auto_id, data_set_max_level=''),
                ),
                Field('fodder', css_class='checkbox'),
                Field('in_storage', css_class='checkbox'),
                Field('ignore_for_fusion', css_class='checkbox'),
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
        fields = ('monster', 'stars', 'level', 'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes')


class BulkAddMonsterInstanceFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BulkAddMonsterInstanceFormset, self).__init__(*args, **kwargs)
        self.queryset = MonsterInstance.objects.none()


class BulkAddMonsterInstanceForm(autocomplete_light.ModelForm):
    monster = autocomplete_light.ModelChoiceField('MonsterAutocomplete')

    def __init__(self, *args, **kwargs):
        super(BulkAddMonsterInstanceForm, self).__init__(*args, **kwargs)
        self.fields['monster'].required = False

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            HTML('<td>'),
            InlineField('monster', data_stars_field=self['stars'].auto_id, data_set_stars=''),
            HTML('</td><td>'),
            InlineField('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
            HTML('</td><td>'),
            FieldWithButtons(
                Field('level', value=1, min=1, max=40),
                StrictButton("Max", name="Set_Max_Level", data_stars_field=self['stars'].auto_id, data_level_field=self['level'].auto_id, data_set_max_level=''),
            ),
            HTML('</td><td>'),
            Field('in_storage'),
            HTML('</td><td>'),
            Field('fodder'),
            HTML('</td>'),
        )

    class Meta:
        model = MonsterInstance
        fields = ('monster', 'stars', 'level', 'in_storage', 'fodder')


class EditMonsterInstanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Field('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                FieldWithButtons(
                    'level',
                    StrictButton("Max", name="Set_Max_Level", data_stars_field=self['stars'].auto_id, data_level_field=self['level'].auto_id, data_set_max_level=''),
                    value=1, min=1, max=40,
                ),
                Field('fodder', css_class='checkbox'),
                Field('in_storage', css_class='checkbox'),
                Field('ignore_for_fusion', css_class='checkbox'),
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
        exclude = ('owner', 'monster', 'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level')


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


class EditTeamGroupForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditTeamGroupForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name'),
            FormActions(
                Submit('save', 'Save', css_class='btn btn-primary'),
                HTML("""<a href="{{ return_path }}" class="btn btn-link">Cancel</a>"""),
                HTML("""<a href="{% url 'herders:team_group_delete' profile_name=profile_name group_id=group_id%}" class="btn btn-danger pull-right">Delete</a>"""),
            ),
        )

    class Meta:
        model = TeamGroup
        exclude = ('id', 'owner')


class DeleteTeamGroupForm(forms.Form):
    reassign_group = forms.ModelChoiceField(
        queryset=TeamGroup.objects.all(),
        required=False,
        label="Reassign teams in this group to:"
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
