from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from bestiary.models import Monster, Effect, LeaderSkill
from .models import MonsterInstance, MonsterTag, MonsterPiece, Summoner, TeamGroup, Team, RuneInstance

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden, Reset
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton, InlineField, Alert

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
        help_text='Used to link to your profile to others: http://swarfarm.com/profile/&lt;username&gt;/',
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
        self.helper.form_class = 'ajax-form'
        self.helper.layout = Layout(
            Div(
                Div(
                    PrependedText('storage_magic_low', '<img src="' + STATIC_URL_PREFIX + 'essences/magic_low.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4  prepended-image-group',
                ),
                Div(
                    PrependedText('storage_magic_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/magic_mid.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4  prepended-image-group',
                ),
                Div(
                    PrependedText('storage_magic_high', '<img src="' + STATIC_URL_PREFIX + 'essences/magic_high.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4  prepended-image-group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_fire_low', '<img src="' + STATIC_URL_PREFIX + 'essences/fire_low.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_fire_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/fire_mid.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_fire_high', '<img src="' + STATIC_URL_PREFIX + 'essences/fire_high.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_water_low', '<img src="' + STATIC_URL_PREFIX + 'essences/water_low.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_water_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/water_mid.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_water_high', '<img src="' + STATIC_URL_PREFIX + 'essences/water_high.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_wind_low', '<img src="' + STATIC_URL_PREFIX + 'essences/wind_low.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_wind_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/wind_mid.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_wind_high', '<img src="' + STATIC_URL_PREFIX + 'essences/wind_high.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_light_low', '<img src="' + STATIC_URL_PREFIX + 'essences/light_low.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_light_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/light_mid.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_light_high', '<img src="' + STATIC_URL_PREFIX + 'essences/light_high.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                css_class='row',
            ),
            Div(
                Div(
                    PrependedText('storage_dark_low', '<img src="' + STATIC_URL_PREFIX + 'essences/dark_low.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_dark_mid', '<img src="' + STATIC_URL_PREFIX + 'essences/dark_mid.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                Div(
                    PrependedText('storage_dark_high', '<img src="' + STATIC_URL_PREFIX + 'essences/dark_high.png" class="prepended-image"/>', min=0),
                    css_class='col-md-4 prepended-image-group',
                ),
                css_class='row',
            ),
            FormActions(
                Submit('save', 'Save'),
            ),
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


class FilterMonsterForm(forms.Form):
    name__icontains = forms.CharField(
        label='Monster Name',
        max_length=100,
        required=False,
    )
    base_stars = forms.MultipleChoiceField(
        choices=Monster.STAR_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    element = forms.MultipleChoiceField(
        label='Element',
        choices=Monster.ELEMENT_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    archetype = forms.MultipleChoiceField(
        label='Archetype',
        choices=Monster.TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    is_awakened = forms.NullBooleanField(label='Is Awakened', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    fusion_food = forms.NullBooleanField(label='Fusion Food', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    leader_skill__attribute = forms.MultipleChoiceField(
        label='Leader Skill Stat',
        choices=LeaderSkill.ATTRIBUTE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    leader_skill__area = forms.MultipleChoiceField(
        label='Leader Skill Stat',
        choices=LeaderSkill.AREA_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    buffs = forms.MultipleChoiceField(
        label='Buffs',
        choices=Effect.buff_effect_choices.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    debuffs = forms.MultipleChoiceField(
        label='Debuffs',
        choices=Effect.debuff_effect_choices.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    other_effects = forms.MultipleChoiceField(
        label='Other Effects',
        choices=Effect.other_effect_choices.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    page = forms.IntegerField(required=False)
    sort = forms.CharField(required=False)

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'FilterBestiaryForm'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-1 text-right'
    helper.field_class = 'col-md-11 no-left-gutter'
    helper.layout = Layout(
        Field('name__icontains', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('base_stars', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('element', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('archetype', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('is_awakened', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('fusion_food', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('leader_skill__attribute', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('leader_skill__area', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('buffs', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/skill_button_checkbox_select.html'),
        Field('debuffs', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/skill_button_checkbox_select.html'),
        Field('other_effects', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('page', value=1, type='hidden'),
        Field('sort', value='', type='hidden'),
    )

    def clean(self):
        super(FilterMonsterForm, self).clean()

        # Coalesce the effect fields into a single one that the filter can understand
        selected_buff_effects = self.cleaned_data.get('buffs')
        selected_debuff_effects = self.cleaned_data.get('debuffs')
        selected_other_effects = self.cleaned_data.get('other_effects')
        self.cleaned_data['skills__skill_effect__pk'] = selected_buff_effects + selected_debuff_effects + selected_other_effects


# MonsterInstance Forms
class AddMonsterInstanceForm(autocomplete_light.ModelForm):
    monster = autocomplete_light.ModelChoiceField('MonsterAutocomplete')

    def __init__(self, *args, **kwargs):
        super(AddMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'ajax-form'
        self.helper.layout = Layout(
            Field(
                'monster',
                data_toggle='popover',
                data_trigger='focus',
                data_container='body',
                title='Autocomplete Tips',
                data_content="Enter the monster's awakened or unawakened name (either will work). To further narrow results, type the element too. Example: \"Raksha water\" will list water Rakshasa and Su",
                data_stars_field=self['stars'].auto_id,
                data_fodder_field=self['fodder'].auto_id,
                data_priority_field=self['priority'].auto_id,
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
            FormActions(
                Submit('save', 'Save', css_class='btn btn-primary'),
                Button('cancel', 'Cancel', css_class='btn btn-link', data_dismiss='modal')
            ),
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
            InlineField(
                'monster',
                data_stars_field=self['stars'].auto_id,
                data_fodder_field=self['fodder'].auto_id,
                data_set_stars=''
            ),
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

        self.fields['ignore_for_fusion'].label = 'Do not use as fusion ingredient'

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'ajax-form'

        self.helper.layout = Layout(
            Div(
                Field('stars', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                FieldWithButtons(
                    Field('level', value=1, min=1, max=40),
                    StrictButton("Max", name="Set_Max_Level", data_stars_field=self['stars'].auto_id, data_level_field=self['level'].auto_id, data_set_max_level=''),
                ),
                Field('fodder', css_class='checkbox'),
                Field('in_storage', css_class='checkbox'),
                Field('ignore_for_fusion', css_class='checkbox'),
                'skill_1_level',
                'skill_2_level',
                'skill_3_level',
                'skill_4_level',
                'tags',
                'priority',
                Field('notes'),
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    HTML("""<button class="btn btn-link" data-dismiss="modal">Cancel</button>"""),
                ),
            )
        )

    class Meta:
        model = MonsterInstance
        fields = ('stars', 'level', 'fodder', 'in_storage', 'ignore_for_fusion', 'priority',
                  'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level', 'notes', 'tags')
        widgets = {
            'tags': autocomplete_light.MultipleChoiceWidget('MonsterTagAutocomplete')
        }


class PowerUpMonsterInstanceForm(forms.Form):
    monster = autocomplete_light.ModelMultipleChoiceField('MonsterInstanceAutocomplete')
    monster.label = 'Material Monsters'
    monster.required = False

    ignore_evolution = forms.BooleanField(
        label='Ignore evolution error checking',
        required=False,
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'ajax-form'
    helper.layout = Layout(
        Field('monster'),
        Field('ignore_evolution'),
        FormActions(
            Submit('power_up', 'Power Up', css_class='btn btn-primary'),
            Submit('evolve', 'Evolve', css_class='btn btn-primary'),
        )
    )


class AwakenMonsterInstanceForm(forms.Form):
    subtract_materials = forms.BooleanField(
        label='Subtract Materials from stock (Insufficient quantities will be reduced to 0)',
        required=False
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'ajax-form'
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


class FilterMonsterInstanceForm(forms.Form):
    monster__name__icontains = forms.CharField(
        label='Monster Name',
        max_length=100,
        required=False,
    )
    tags__pk = forms.MultipleChoiceField(
        label='Tags',
        choices=MonsterTag.objects.values_list('pk', 'name'),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    stars = forms.MultipleChoiceField(
        choices=Monster.STAR_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    monster__element = forms.MultipleChoiceField(
        label='Element',
        choices=Monster.ELEMENT_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    monster__archetype = forms.MultipleChoiceField(
        label='Archetype',
        choices=Monster.TYPE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    priority = forms.MultipleChoiceField(
        label='Priority',
        choices=MonsterInstance.PRIORITY_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    monster__is_awakened = forms.NullBooleanField(label='Is Awakened', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    fodder = forms.NullBooleanField(label='Fodder', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    in_storage = forms.NullBooleanField(label='Storage', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    monster__fusion_food = forms.NullBooleanField(label='Fusion Food', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    monster__leader_skill__attribute = forms.MultipleChoiceField(
        label='Leader Skill Stat',
        choices=LeaderSkill.ATTRIBUTE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    monster__leader_skill__area = forms.MultipleChoiceField(
        label='Leader Skill Stat',
        choices=LeaderSkill.AREA_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    buffs = forms.MultipleChoiceField(
        label='Buffs',
        choices=Effect.buff_effect_choices.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    debuffs = forms.MultipleChoiceField(
        label='Debuffs',
        choices=Effect.debuff_effect_choices.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    other_effects = forms.MultipleChoiceField(
        label='Other Effects',
        choices=Effect.other_effect_choices.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'FilterInventoryForm'
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-md-1 text-right'
    helper.field_class = 'col-md-11 no-left-gutter'
    helper.layout = Layout(
        Field('monster__name__icontains', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('tags__pk', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('stars', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('monster__element', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('monster__archetype', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('monster__is_awakened', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('priority', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('fodder', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('in_storage', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('monster__fusion_food', css_class='auto-submit short', wrapper_class='form-group-sm form-group-condensed'),
        Field('monster__leader_skill__attribute', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('monster__leader_skill__area', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
        Field('buffs', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/skill_button_checkbox_select.html'),
        Field('debuffs', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/skill_button_checkbox_select.html'),
        Field('other_effects', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed', template='crispy/button_checkbox_select.html'),
    )

    def clean(self):
        super(FilterMonsterInstanceForm, self).clean()

        # Coalesce the effect fields into a single one that the filter can understand
        selected_buff_effects = self.cleaned_data.get('buffs')
        selected_debuff_effects = self.cleaned_data.get('debuffs')
        selected_other_effects = self.cleaned_data.get('other_effects')
        self.cleaned_data['monster__skills__skill_effect__pk'] = selected_buff_effects + selected_debuff_effects + selected_other_effects


# MonsterPiece forms
class MonsterPieceForm(autocomplete_light.ModelForm):
    monster = autocomplete_light.ModelChoiceField('MonsterAutocomplete')

    def __init__(self, *args, **kwargs):
        super(MonsterPieceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'ajax-form'
        self.helper.layout = Layout(
            Field(
                'monster',
                data_toggle='popover',
                data_trigger='focus',
                data_container='body',
                title='Autocomplete Tips',
                data_content="Enter the monster's awakened or unawakened name (either will work). To further narrow results, type the element too. Example: \"Raksha water\" will list water Rakshasa and Su",
            ),
            Field('pieces'),
            FormActions(
                Submit('save', 'Save', css_class='btn btn-primary'),
                Button('cancel', 'Cancel', css_class='btn btn-link', data_dismiss='modal')
            ),
        )

    class Meta:
        model = MonsterPiece
        fields = ('monster', 'pieces',)


# Team Forms
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

    def clean(self):
        from django.core.exceptions import ValidationError

        # Check that leader is not also in the roster
        leader = self.cleaned_data.get('leader')
        roster = self.cleaned_data.get('roster')

        if leader in roster:
            raise ValidationError(
                'Leader cannot be included in the roster as well',
                code='leader_in_roster'
            )

        super(EditTeamForm, self).clean()


# Rune Forms
class AddRuneInstanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddRuneInstanceForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = self.fields['type'].choices[1:]  # Remove the empty '----' option from the list
        self.fields['main_stat'].label = False
        self.fields['main_stat_value'].label = False
        self.fields['innate_stat'].label = False
        self.fields['innate_stat_value'].label = False
        self.fields['substat_1'].label = False
        self.fields['substat_1_value'].label = False
        self.fields['substat_1_craft'].label = False
        self.fields['substat_2'].label = False
        self.fields['substat_2_value'].label = False
        self.fields['substat_2_craft'].label = False
        self.fields['substat_3'].label = False
        self.fields['substat_3_value'].label = False
        self.fields['substat_3_craft'].label = False
        self.fields['substat_4'].label = False
        self.fields['substat_4_value'].label = False
        self.fields['substat_4_craft'].label = False
        self.fields['assigned_to'].label = False

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'addRuneForm'
        self.helper.form_class = 'ajax-form'
        self.helper.layout = Layout(
            Div(
                Field('type', template="crispy/rune_button_radio_select.html"),
                css_class='col-md-2',
            ),
            Div(
                Div(
                    Div(Field('slot', placeholder='1-6'), css_class='col-md-3'),
                    Div(Field('stars', placeholder='1-6'), css_class='col-md-4'),
                    Div(Field('level', placeholder='0-15'), css_class='col-md-4'),
                    css_class='row'
                ),
                Div(
                    Div(
                        HTML('<label class="col-md-2 control-label">Main Stat</label>'),
                        Field('main_stat', wrapper_class='col-md-4 inline-horizontal'),
                        Field('main_stat_value', wrapper_class='col-md-3 inline-horizontal', placeholder='Value'),
                        css_class='form-group form-group-condensed',
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Innate Stat</label>'),
                        Field('innate_stat', wrapper_class='col-md-4 inline-horizontal'),
                        Field('innate_stat_value', wrapper_class='col-md-3 inline-horizontal', placeholder='Value'),
                        css_class='form-group form-group-condensed',
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Substat 1</label>'),
                        Field('substat_1', wrapper_class='col-md-4 inline-horizontal'),
                        Field('substat_1_value', wrapper_class='col-md-3 inline-horizontal', placeholder='Value'),
                        Field('substat_1_craft', wrapper_class='col-md-3 inline-horizontal'),
                        css_class='form-group form-group-condensed',
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Substat 2</label>'),
                        Field('substat_2', wrapper_class='col-md-4 inline-horizontal'),
                        Field('substat_2_value', wrapper_class='col-md-3 inline-horizontal', placeholder='Value'),
                        Field('substat_2_craft', wrapper_class='col-md-3 inline-horizontal'),
                        css_class='form-group form-group-condensed',
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Substat 3</label>'),
                        Field('substat_3', wrapper_class='col-md-4 inline-horizontal'),
                        Field('substat_3_value', wrapper_class='col-md-3 inline-horizontal', placeholder='Value'),
                        Field('substat_3_craft', wrapper_class='col-md-3 inline-horizontal'),
                        css_class='form-group form-group-condensed',
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Substat 4</label>'),
                        Field('substat_4', wrapper_class='col-md-4 inline-horizontal'),
                        Field('substat_4_value', wrapper_class='col-md-3 inline-horizontal', placeholder='Value'),
                        Field('substat_4_craft', wrapper_class='col-md-3 inline-horizontal'),
                        css_class='form-group form-group-condensed',
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Assign To</label>'),
                        Div(
                            Field('assigned_to', wrapper_class='col-md-4'),
                        ),
                        css_class='form-group form-group-condensed',
                    ),
                    css_class='form-horizontal',
                ),
                css_class='col-md-10',
            ),
            Div(css_class='clearfix'),
            FormActions(
                Submit('save', 'Save'),
            ),
        )

    class Meta:
        model = RuneInstance
        fields = (
            'type', 'stars', 'level', 'slot',
            'main_stat', 'main_stat_value',
            'innate_stat', 'innate_stat_value',
            'substat_1', 'substat_1_value', 'substat_1_craft',
            'substat_2', 'substat_2_value', 'substat_2_craft',
            'substat_3', 'substat_3_value', 'substat_3_craft',
            'substat_4', 'substat_4_value', 'substat_4_craft',
            'assigned_to',
        )
        widgets = {
            'assigned_to': autocomplete_light.ChoiceWidget('MonsterInstanceAutocomplete'),
        }


class AssignRuneForm(forms.Form):
    type = forms.MultipleChoiceField(
        choices=RuneInstance.TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    level__gte = forms.IntegerField(
        label="Minimum Level",
        min_value=0,
        max_value=15,
        required=False,
    )
    stars__gte = forms.IntegerField(
        label="Minimum Stars",
        required=False
    )
    stars__lte = forms.IntegerField(
        label="Maximum Stars",
        required=False
    )
    slot = forms.IntegerField(
        min_value=1,
        max_value=6,
        required=False
    )

    has_hp = forms.NullBooleanField(label='Has HP', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_atk = forms.NullBooleanField(label='Has ATK', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_def = forms.NullBooleanField(label='Has DEF', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_crit_rate = forms.NullBooleanField(label='Has CRI Rate', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_crit_dmg = forms.NullBooleanField(label='Has CRI Dmg', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_speed = forms.NullBooleanField(label='Has SPD', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_resist = forms.NullBooleanField(label='Has RES', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_accuracy = forms.NullBooleanField(label='Has ACC', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'AssignRuneForm'
    helper.layout = Layout(
        FormActions(
            StrictButton('Create New', id='addNewRune', css_class='btn btn-primary btn-block'),
            Reset('Reset Form', 'Reset Filters', css_class='btn btn-danger btn-block'),
        ),
        Div(
            Div(
                Field('type', css_class='auto-submit', template='crispy/rune_button_checkbox_select_notext.html'),
                Field('has_hp', css_class='auto-submit'),
                Field('has_atk', css_class='auto-submit'),
                Field('has_def', css_class='auto-submit'),
                Field('has_crit_rate', css_class='auto-submit'),
                Field('has_crit_dmg', css_class='auto-submit'),
                Field('has_speed', css_class='auto-submit'),
                Field('has_resist', css_class='auto-submit'),
                Field('has_accuracy', css_class='auto-submit'),
                css_class='col-md-6',
            ),
            Div(
                Field('level__gte', css_class='auto-submit'),
                Field('stars__gte', css_class='rating hidden auto-submit', value=1, data_start=0, data_stop=6, data_stars=6),
                Field('stars__lte', css_class='rating hidden auto-submit', value=6, data_start=0, data_stop=6, data_stars=6),
                css_class='col-md-6',
            ),
            css_class='row',
        ),
        Field('slot', type='hidden', css_class='auto-submit'),
    )


class FilterRuneForm(forms.Form):
    type = forms.MultipleChoiceField(
        choices=RuneInstance.TYPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    main_stat = forms.MultipleChoiceField(
        choices=RuneInstance.STAT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    level__gte = forms.IntegerField(
        label="Minimum Level",
        min_value=0,
        max_value=15,
        required=False,
    )
    level__lte = forms.IntegerField(
        label="Maximum Level",
        min_value=0,
        max_value=15,
        required=False,
    )
    stars__gte = forms.IntegerField(
        label="Minimum Stars",
        required=False
    )
    stars__lte = forms.IntegerField(
        label="Maximum Stars",
        required=False
    )
    slot = forms.IntegerField(
        min_value=1,
        max_value=6,
        required=False
    )
    assigned_to = forms.NullBooleanField(
        label="Is Assigned",
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    has_hp = forms.NullBooleanField(label='Has HP', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_atk = forms.NullBooleanField(label='Has ATK', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_def = forms.NullBooleanField(label='Has DEF', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_crit_rate = forms.NullBooleanField(label='Has CRI Rate', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_crit_dmg = forms.NullBooleanField(label='Has CRI Dmg', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_speed = forms.NullBooleanField(label='Has SPD', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_resist = forms.NullBooleanField(label='Has RES', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))
    has_accuracy = forms.NullBooleanField(label='Has ACC', required=False, widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))))

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'FilterInventoryForm'
    helper.layout = Layout(
        Div(
            Div(
                Field('main_stat', css_class='auto-submit'),
                css_class='col-sm-1',
            ),
            Div(
                Div(
                    Div(
                        Field('type', css_class='auto-submit', template='crispy/rune_button_checkbox_select_notext.html'),
                        css_class='col-sm-12',
                    ),
                    css_class='row'
                ),
                Div(
                    Div(
                        Div(
                            Field('slot', css_class='auto-submit'),
                            css_class='pull-left condensed',
                        ),
                        Div(
                            Field('assigned_to', css_class='auto-submit'),
                            css_class='pull-left condensed',
                        ),
                        Div(
                            Field('level__gte', css_class='auto-submit'),
                            css_class='pull-left condensed',
                        ),
                        Div(
                            Field('level__lte', css_class='auto-submit'),
                            css_class='pull-left condensed',
                        ),
                        Div(
                            Field('stars__gte', css_class='rating hidden', value=1, data_start=0, data_stop=6, data_stars=6),
                            css_class='pull-left condensed'
                        ),
                        Div(
                            Field('stars__lte', css_class='rating hidden', value=6, data_start=0, data_stop=6, data_stars=6),
                            css_class='pull-left condensed'
                        ),
                        css_class='col-sm-12',
                    ),
                    css_class='row',
                ),
                Div(
                    Div(
                        Div(Field('has_hp', css_class='auto-submit'), css_class='pull-left condensed'),
                        Div(Field('has_atk', css_class='auto-submit'), css_class='pull-left condensed'),
                        Div(Field('has_def', css_class='auto-submit'), css_class='pull-left condensed'),
                        Div(Field('has_crit_rate', css_class='auto-submit'), css_class='pull-left condensed'),
                        Div(Field('has_crit_dmg', css_class='auto-submit'), css_class='pull-left condensed'),
                        Div(Field('has_speed', css_class='auto-submit'), css_class='pull-left condensed'),
                        Div(Field('has_resist', css_class='auto-submit'), css_class='pull-left condensed'),
                        Div(Field('has_accuracy', css_class='auto-submit'), css_class='pull-left condensed'),
                        css_class='col-sm-12',
                    ),
                    css_class='row',
                ),
                css_class='col-sm-10',
            ),
            css_class='row',
        ),
    )


class ImportRuneForm(forms.Form):
    json_data = forms.CharField(
        max_length=999999,
        required=True,
        label='Paste Rune Data',
        help_text=mark_safe('Data is exported from the <a href="http://swrunes.all.my/" target="_blank">Summoners War Rune Database and Optimizer</a>'),
        widget=forms.Textarea(),
    )

    helper = FormHelper()
    helper.form_tag = False
    helper.layout = Layout(
        Alert('You can only import runes. Importing will create new runes, not update your current runes. Monsters and saved builds from the spreadsheet are ignored.', css_class='alert-warning'),
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


class ExportRuneForm(forms.Form):
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
