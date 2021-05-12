from itertools import chain

from captcha.fields import ReCaptchaField
from crispy_forms.bootstrap import FormActions, FieldWithButtons, StrictButton, InlineField, InlineRadios
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden, Reset, Fieldset
from dal import autocomplete
from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.contrib.postgres.forms import SplitArrayField
from django.core.validators import RegexValidator, ValidationError
from django.db.models.fields import BLANK_CHOICE_DASH
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from bestiary.fields import AdvancedSelectMultiple
from bestiary.models import Monster, SkillEffect, LeaderSkill, ScalingStat, Dungeon, Level, GameItem
from bestiary.widgets import ElementSelectMultipleWidget, EffectSelectMultipleWidget
from data_log.models import RiftDungeonLog, WorldBossLog, CraftRuneLog, MagicBoxCraft
from .models import MonsterInstance, MonsterTag, MonsterPiece, Summoner, TeamGroup, Team, \
    RuneInstance, RuneCraftInstance, BuildingInstance, ArtifactInstance

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
            FormActions(Submit('login', 'Log In', css_class='float-right')),
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
            FormActions(Submit('submit', 'Submit', css_class='float-right')),
        )


class CrispyPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(CrispyPasswordResetForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_action = 'password_reset'
        self.helper.layout = Layout(
            Field('email'),
            FormActions(Submit('submit', 'Submit', css_class='float-right')),
        )


class CrispySetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(CrispySetPasswordForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('new_password1'),
            Field('new_password2'),
            FormActions(Submit('submit', 'Submit', css_class='float-right')),
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
        FormActions(Submit('change', 'Change', css_class='float-right'))
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
    dark_mode = forms.BooleanField(label='Dark Mode', required=False)
    server = forms.ChoiceField(label="Summoner's War Server", choices=[(None, '---')] + Summoner.SERVER_CHOICES, required=False)
    captcha = ReCaptchaField()

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_action = 'herders:register'
    helper.layout = Layout(
        Field('username', css_class='input-sm'),
        Field('password', css_class='input-sm'),
        Field('email', css_class='input-sm'),
        Field('summoner_name', css_class='input-sm'),
        Field('server'),
        Field('is_public'),
        Field('dark_mode'),
        Field('captcha'),
        FormActions(Submit('register', 'Register', css_class='float-right'))
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
                Field('dark_mode'),
                Field('timezone'),
                Field('server'),
            ),
        )

    class Meta:
        model = Summoner
        fields = (
            'summoner_name',
            'public',
            'dark_mode',
            'timezone',
            'server',
        )
        labels = {
            'summoner_name': "Summoner's War Account Name",
            'public': 'Make my SWARFARM account visible to others',
            'dark_mode': 'Dark Mode',
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


# Profile forms
class EditBuildingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditBuildingForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'ajax-form'
        self.helper.include_media = False
        # self.helper.form_action must be set in view
        self.helper.layout = Layout(
            Field('level', autocomplete='off'),
            FormActions(
                Submit('save', 'Save', css_class='btn-success float-right')
            )
        )

    class Meta:
        model = BuildingInstance
        fields = [
            'level',
        ]


# MonsterInstance Forms
class AddMonsterInstanceForm(forms.ModelForm):
    monster = forms.ModelChoiceField(
        queryset=Monster.objects.all(),
        widget=autocomplete.ModelSelect2(
            url='bestiary-monster-autocomplete',
        )
    )

    def __init__(self, *args, **kwargs):
        super(AddMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'ajax-form'
        self.helper.form_id = 'id_AddMonsterInstanceForm'
        self.helper.include_media = False
        self.helper.layout = Layout(
            Field(
                'monster',
                data_stars_field=self['stars'].auto_id,
                data_fodder_field=self['fodder'].auto_id,
                data_priority_field=self['priority'].auto_id,
                data_custom_name_field='div_{}'.format(self['custom_name'].auto_id),
                data_set_stars='',
            ),
            Field('custom_name', wrapper_class='visually-hidden'),
            Field('stars', value=1, data_start=0, data_stop=6, data_stars=6),
            FieldWithButtons(
                Field('level', value=1, min=1, max=40, css_class='form-control'),
                StrictButton("Max", name="Set_Max_Level", data_stars_field=self['stars'].auto_id, data_level_field=self['level'].auto_id, data_set_max_level='', css_class='btn btn-outline-dark'),
                wrapper_class='btn-group',
            ),
            Field('fodder', css_class='checkbox'),
            Field('in_storage', css_class='checkbox'),
            Field('ignore_for_fusion', css_class='checkbox'),
            Field('priority',),
            Field('notes'),
            FormActions(
                Button('cancel', 'Cancel', css_class='btn btn-link', data_bs_dismiss='modal'),
                Submit('save', 'Save'),
                css_class='float-right',
            ),
        )

    class Meta:
        model = MonsterInstance
        fields = ('monster', 'custom_name', 'stars', 'level', 'fodder', 'in_storage', 'ignore_for_fusion', 'priority', 'notes')
        labels = {
            'ignore_for_fusion': mark_safe('<i class="fas fa-lock"></i>Locked'),
        }


class BulkAddMonsterInstanceFormset(BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        super(BulkAddMonsterInstanceFormset, self).__init__(*args, **kwargs)
        self.queryset = MonsterInstance.objects.none()


class BulkAddMonsterInstanceForm(forms.ModelForm):
    monster = forms.ModelChoiceField(
        queryset=Monster.objects.all(),
        widget=autocomplete.ModelSelect2(url='bestiary-monster-autocomplete')
    )

    class Meta:
        model = MonsterInstance
        fields = ('monster', 'stars', 'level', 'in_storage', 'fodder')

    def __init__(self, *args, **kwargs):
        super(BulkAddMonsterInstanceForm, self).__init__(*args, **kwargs)
        self.fields['monster'].required = False

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.form_show_labels = False
        self.helper.disable_csrf = True
        self.helper.include_media = False
        self.helper.layout = Layout(
            HTML('<td width="250px">'),
            InlineField(
                'monster',
                data_stars_field=self['stars'].auto_id,
                data_fodder_field=self['fodder'].auto_id,
                data_set_stars='',
                wrapper_class='full-width',
            ),
            HTML('</td><td>'),
            InlineField('stars', css_class='rating visually-hidden form-control', value=1, data_start=0, data_stop=6, data_stars=6),
            HTML('</td><td>'),
            FieldWithButtons(
                Field('level', value=1, min=1, max=40, css_class='form-control'),
                StrictButton("Max", name="Set_Max_Level", data_stars_field=self['stars'].auto_id, data_level_field=self['level'].auto_id, data_set_max_level='', css_class="btn-outline-dark"),
                wrapper_class='btn-group',
            ),
            HTML('</td><td>'),
            Field('in_storage', css_class='form-check-input p-0'),
            HTML('</td><td>'),
            Field('fodder', css_class='form-check-input p-0'),
            HTML('</td>'),
        )

    def has_changed(self):
        return all(required_field in self.changed_data for required_field in ['monster', 'stars', 'level'])


class EditMonsterInstanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'ajax-form'
        self.helper.include_media = False

        self.helper.layout = Layout(
            Div(
                Field('custom_name'),
                Field('stars', value=1, data_start=0, data_stop=6, data_stars=6),
                FieldWithButtons(
                    Field('level', value=1, min=1, max=40, css_class='form-control'),
                    StrictButton("Max", name="Set_Max_Level", data_stars_field=self['stars'].auto_id, data_level_field=self['level'].auto_id, data_set_max_level='', css_class='btn-outline-dark'),
                    wrapper_class='btn-group',
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
                    HTML("""<button type="button" class="btn btn-link" data-bs-dismiss="modal">Cancel</button>"""),
                    Submit('save', 'Save', css_class='btn btn-primary'),
                    css_class='float-right',
                ),
            )
        )

    class Meta:
        model = MonsterInstance
        fields = ('custom_name', 'stars', 'level', 'fodder', 'in_storage', 'ignore_for_fusion', 'priority',
                  'skill_1_level', 'skill_2_level', 'skill_3_level', 'skill_4_level', 'notes', 'tags')
        labels = {
            'ignore_for_fusion': mark_safe('<i class="fas fa-lock"></i>Locked'),
        }
        widgets = {
            'tags': autocomplete.ModelSelect2Multiple(url='monster-tag-autocomplete')
        }


class PowerUpMonsterInstanceForm(forms.Form):
    monster = forms.ModelMultipleChoiceField(
        queryset=MonsterInstance.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(url='monster-instance-autocomplete')
    )
    monster.label = 'Material Monsters'
    monster.required = False

    ignore_evolution = forms.BooleanField(
        label='Ignore evolution error checking',
        required=False,
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_class = 'ajax-form'
    helper.include_media = False
    helper.layout = Layout(
        Field('monster'),
        Field('ignore_evolution'),
        FormActions(
            Submit('evolve', 'Evolve', css_class='btn btn-primary'),
            Submit('power_up', 'Power Up', css_class='btn btn-primary'),
            css_class='float-right',
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
                HTML("""<a href="{{ return_path }}" class="btn btn-link">Cancel</a>"""),
                Submit('awaken', 'Awaken', css_class='btn btn-primary'),
                css_class='float-right',
            ),
        )
    )


class FilterMonsterInstanceForm(forms.Form):
    monster__name = forms.CharField(
        label='Monster Name',
        max_length=100,
        required=False,
    )
    tags__pk = forms.ModelMultipleChoiceField(
        label='Tags',
        queryset=MonsterTag.objects.all(),
        required=False,
    )
    stars = forms.CharField(
        label="Stars",
        required=False,
    )
    level = forms.CharField(
        label="Level",
        required=False,
    )
    monster__natural_stars = forms.CharField(
        label="Natural Stars",
        required=False,
    )
    monster__element = forms.MultipleChoiceField(
        label='Element',
        choices=Monster.ELEMENT_CHOICES,
        required=False,
        widget=ElementSelectMultipleWidget,
    )
    monster__archetype = forms.MultipleChoiceField(
        label='Archetype',
        choices=Monster.ARCHETYPE_CHOICES,
        required=False,
    )
    priority = forms.MultipleChoiceField(
        label='Priority',
        choices=MonsterInstance.PRIORITY_CHOICES,
        required=False,
    )
    monster__awaken_level = forms.MultipleChoiceField(
        label='Awaken Level',
        required=False,
        choices=Monster.AWAKEN_CHOICES[:3],  # Remove "incomplete" option
    )
    fodder = forms.ChoiceField(
        label='Fodder',
        required=False,
        choices=[(None, 'N/A'), (True, 'Yes'), (False, 'No')],
        widget=forms.RadioSelect,
    )
    in_storage = forms.ChoiceField(
        label='Storage',
        required=False,
        choices=[(None, 'N/A'), (True, 'Yes'), (False, 'No')],
        widget=forms.RadioSelect,
    )
    monster__fusion_food = forms.ChoiceField(
        label='Fusion Food',
        required=False,
        choices=[(None, 'N/A'), (True, 'Yes'), (False, 'No')],
        widget=forms.RadioSelect,
    )
    monster__leader_skill__attribute = forms.MultipleChoiceField(
        label='Stat',
        choices=LeaderSkill.ATTRIBUTE_CHOICES,
        required=False,
    )
    monster__leader_skill__area = forms.MultipleChoiceField(
        label='Area',
        choices=LeaderSkill.AREA_CHOICES,
        required=False,
    )
    monster__skills__scaling_stats__pk = forms.ModelMultipleChoiceField(
        label='Scales With',
        queryset=ScalingStat.objects.all(),
        required=False,
    )
    monster__skills__cooltime = forms.CharField(
        label="Cooldown",
        required=False,
    )
    monster__skills__hits = forms.CharField(
        label="Number of Hits",
        required=False,
    )
    monster__skills__passive = forms.NullBooleanField(
        label="Passive",
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    monster__skills__aoe = forms.NullBooleanField(
        label="AOE",
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    buff_debuff_effects = AdvancedSelectMultiple(
        label='Buffs/Debuffs',
        queryset=SkillEffect.objects.exclude(icon_filename=''),
        required=False,
        widget=EffectSelectMultipleWidget,
    )
    other_effects = forms.ModelMultipleChoiceField(
        label='Other Effects',
        queryset=SkillEffect.objects.filter(icon_filename=''),
        required=False,
    )
    effects_logic = forms.BooleanField(
        label=mark_safe('<i class="fas fa-info-circle" data-bs-toggle="tooltip" title="Whether all effect filters must be on ONE individual skill or can be spread across ANY skill in a monster\'s skill set."></i>'),
        required=False,
        initial=True,
    )

    helper = FormHelper()
    helper.form_method = 'get'
    helper.form_id = 'FilterInventoryForm'
    helper.layout = Layout(
        Div(
            Fieldset(
                'General',
                Div(
                    Div(
                        Div(
                            Field('monster__name', wrapper_class='form-group-sm form-group-condensed col-sm-6'),
                            Field(
                                'stars',
                                data_provide='slider',
                                data_slider_min='1',
                                data_slider_max='6',
                                data_slider_value='[1, 6]',
                                data_slider_step='1',
                                data_slider_ticks='[1, 6]',
                                data_slider_ticks_labels='["1", "6"]',
                                wrapper_class='form-group-sm form-group-condensed col-sm-6'
                            ),
                            css_class='row'
                        ),
                        Div(
                            Field(
                                'monster__natural_stars',
                                data_provide='slider',
                                data_slider_min='1',
                                data_slider_max='5',
                                data_slider_value='[1, 5]',
                                data_slider_step='1',
                                data_slider_ticks='[1, 5]',
                                data_slider_ticks_labels='["1", "5"]',
                                wrapper_class='form-group-sm form-group-condensed col-sm-6'
                            ),
                            Field(
                                'level',
                                data_provide='slider',
                                data_slider_min='1',
                                data_slider_max='40',
                                data_slider_value='[1, 40]',
                                data_slider_step='1',
                                data_slider_ticks='[1, 40]',
                                data_slider_ticks_labels='["1", "40"]',
                                wrapper_class='form-group-sm form-group-condensed col-sm-6',
                            ),
                            Field('tags__pk', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-sm-6'),
                            Field('priority', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-sm-6'),
                            Field('monster__archetype', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-sm-6'),
                            Field(
                                'monster__element',
                                css_class='select2',
                                data_result_template='iconSelect2Template',
                                data_selection_template='iconSelect2Template',
                                wrapper_class='form-group-sm form-group-condensed col-sm-6',
                            ),
                            css_class='row',
                        ),
                        css_class='col-lg-8 col-md-6'
                    ),
                    Div(
                        Field(
                            'monster__awaken_level',
                            css_class='select2',
                        ),
                        InlineRadios('fodder', wrapper_class='form-group-sm form-group-condensed'),
                        InlineRadios('in_storage', wrapper_class='form-group-sm form-group-condensed'),
                        InlineRadios('monster__fusion_food', wrapper_class='form-group-sm form-group-condensed'),
                        css_class='col-lg-4 col-md-6'
                    ),
                    css_class='row'
                ),
                css_class='col-md-8'
            ),
            Div(
                Fieldset(
                    'Skills',
                    Div(
                        Field(
                            'buff_debuff_effects',
                            css_class='select2',
                            data_result_template='iconSelect2Template',
                            data_selection_template='iconSelect2Template',
                            wrapper_class='form-group-sm form-group-condensed col-lg-6'
                        ),
                        Field('other_effects', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field('monster__skills__scaling_stats__pk', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field('monster__skills__passive', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field('monster__skills__aoe', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field(
                            'monster__skills__cooltime',
                            data_provide='slider',
                            data_slider_min='0',
                            data_slider_max='13',
                            data_slider_value='[0, 13]',
                            data_slider_step='1',
                            data_slider_ticks='[0, 13]',
                            data_slider_ticks_labels='["0", "13"]',
                            wrapper_class='col-lg-6'
                        ),
                        Field(
                            'monster__skills__hits',
                            data_provide='slider',
                            data_slider_min='0',
                            data_slider_max='7',
                            data_slider_value='[0, 7]',
                            data_slider_step='1',
                            data_slider_ticks='[0, 7]',
                            data_slider_ticks_labels='["0", "7"]',
                            wrapper_class='form-group-sm form-group-condensed col-lg-6'
                        ),
                        Field(
                            'effects_logic',
                            data_toggle='toggle', 
                            data_on='Any Skill', 
                            data_onstyle='dark', 
                            data_off='One Skill', 
                            data_width='125px', 
                            wrapper_class='form-group-sm form-group-condensed col-lg-6 ps-0'
                        ),
                        css_class='row'
                    ),
                ),
                Fieldset(
                    'Leader Skill',
                    Div(
                        Field('monster__leader_skill__attribute', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field('monster__leader_skill__area', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        css_class='row'
                    )
                ),
                css_class='col-md-4'
            ),
            css_class='row',
        ),
        Div(
            Div(
                Submit('apply', 'Apply', css_class='btn-success '),
                css_class='btn-group w-50'
            ),
            Div(
                Button('resetBtn', 'Reset Filters', css_class='btn-outline-danger reset'),
                css_class='btn-group w-50'
            ),
            css_class='btn-group w-100'
        ),
    )

    def clean(self):
        super(FilterMonsterInstanceForm, self).clean()

        # Coalesce the effect fields into a single one that the filter can understand
        buff_debuff_effects = self.cleaned_data.get('buff_debuff_effects')
        other_effects = self.cleaned_data.get('other_effects')
        self.cleaned_data['monster__skills__effect__pk'] = chain(buff_debuff_effects, other_effects)

        # Convert the select fields with None/True/False options into actual boolean values
        choices = {
            'None': None,
            'True': True,
            'False': False,
        }

        self.cleaned_data['monster__is_awakened'] = choices.get(self.cleaned_data.get('monster__is_awakened', 'None'), None)
        self.cleaned_data['fodder'] = choices.get(self.cleaned_data.get('fodder', 'None'), None)
        self.cleaned_data['in_storage'] = choices.get(self.cleaned_data.get('in_storage', 'None'), None)
        self.cleaned_data['monster__fusion_food'] = choices.get(self.cleaned_data.get('monster__fusion_food', 'None'), None)

        # Split the slider ranges into two min/max fields for the automatic filters
        try:
            [min_lv, max_lv] = self.cleaned_data['level'].split(',')
            self.cleaned_data['level__gte'] = int(min_lv)
            self.cleaned_data['level__lte'] = int(max_lv)
        except:
            self.cleaned_data['level__gte'] = None
            self.cleaned_data['level__lte'] = None

        try:
            [min_stars, max_stars] = self.cleaned_data['stars'].split(',')
            self.cleaned_data['stars__gte'] = int(min_stars)
            self.cleaned_data['stars__lte'] = int(max_stars)
        except:
            self.cleaned_data['stars__gte'] = None
            self.cleaned_data['stars__lte'] = None

        try:
            [min_nat_stars, max_nat_stars] = self.cleaned_data['monster__natural_stars'].split(',')
            self.cleaned_data['monster__natural_stars__gte'] = int(min_nat_stars)
            self.cleaned_data['monster__natural_stars__lte'] = int(max_nat_stars)
        except:
            self.cleaned_data['monster__natural_stars__gte'] = None
            self.cleaned_data['monster__natural_stars__lte'] = None


# MonsterPiece forms
class MonsterPieceForm(forms.ModelForm):
    monster = forms.ModelChoiceField(
        queryset=Monster.objects.all(),
        widget=autocomplete.ModelSelect2(url='bestiary-monster-autocomplete')
    )

    def __init__(self, *args, **kwargs):
        super(MonsterPieceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'ajax-form'
        self.helper.include_media = False
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
                Button('cancel', 'Cancel', css_class='btn btn-link', data_bs_dismiss='modal')
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
                    Button('cancel', 'Cancel', css_class='btn btn-link', data_bs_dismiss='modal')
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
                HTML("""<a href="{% url 'herders:team_group_delete' profile_name=profile_name group_id=group_id%}" class="btn btn-danger float-right">Delete</a>"""),
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
    leader = forms.ModelChoiceField(
        queryset=MonsterInstance.objects.none(),  # Override in view
        widget=autocomplete.ModelSelect2(url='monster-instance-autocomplete'),
        required=False,
    )

    roster = forms.ModelMultipleChoiceField(
        queryset=MonsterInstance.objects.none(),  # Override in view
        widget=autocomplete.ModelSelect2Multiple(url='monster-instance-autocomplete'),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(EditTeamForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'EditTeamForm'
        self.helper.include_media = False
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

    def clean(self):
        from django.core.exceptions import ValidationError

        super(EditTeamForm, self).clean()

        # Check that leader is not also in the roster
        leader = self.cleaned_data.get('leader')
        roster = self.cleaned_data.get('roster')

        if leader in roster:
            raise ValidationError(
                'Leader cannot be included in the roster as well',
                code='leader_in_roster'
            )


# Rune Forms
class AddRuneInstanceForm(ModelForm):
    substats = SplitArrayField(
        forms.TypedChoiceField(
            choices=((None, '---------'), ) + RuneInstance.STAT_CHOICES,
            coerce=int,
            empty_value=None,
        ),
        size=4,
        remove_trailing_nulls=True,
        label='Substat',
        required=False,
    )

    substat_values = SplitArrayField(
        forms.IntegerField(required=False),
        size=4,
        remove_trailing_nulls=True,
        label='Value',
        required=False,
    )

    substats_enchanted = SplitArrayField(
        forms.BooleanField(required=False),
        size=4,
        remove_trailing_nulls=True,
        label='Enchanted',
        required=False,
    )

    substats_grind_value = SplitArrayField(
        forms.IntegerField(required=False),
        size=4,
        remove_trailing_nulls=True,
        label='Grind Value',
        required=False,
    )

    class Meta:
        model = RuneInstance
        fields = (
            'type', 'stars', 'level', 'slot', 'ancient',
            'main_stat', 'main_stat_value',
            'innate_stat', 'innate_stat_value',
            'substats', 'substat_values', 'substats_enchanted', 'substats_grind_value',
            'substats', 'substats_enchanted',
            'assigned_to', 'notes', 'marked_for_sale',
        )
        widgets = {
            'assigned_to': autocomplete.ModelSelect2(url='monster-instance-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super(AddRuneInstanceForm, self).__init__(*args, **kwargs)
        self.fields['type'].choices = self.fields['type'].choices[1:]  # Remove the empty '----' option from the list
        self.fields['main_stat'].label = False
        self.fields['main_stat_value'].label = False
        self.fields['innate_stat'].label = False
        self.fields['innate_stat_value'].label = False
        self.fields['assigned_to'].label = False
        self.fields['notes'].label = False

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'addRuneForm'
        self.helper.form_class = 'ajax-form row'
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Field('type', template="crispy/rune_button_radio_select.html"),
                css_class='col-md-3',
            ),
            Div(
                Div(
                    Div(Field('slot', placeholder='1-6', min=1, max=6), css_class='col-md-3'),
                    Div(Field('stars', placeholder='1-6', min=1, max=6), css_class='col-md-3'),
                    Div(Field('level', placeholder='0-15', min=0, max=15), css_class='col-md-3'),
                    Div(Field('ancient'), css_class='col-md-3'),
                    css_class='row'
                ),
                Div(
                    Div(
                        HTML('<label class="col-md-4 control-label">Main Stat</label>'),
                        Field('main_stat', wrapper_class='col-md-4 inline-horizontal'),
                        Field('main_stat_value', wrapper_class='col-md-4 inline-horizontal'),
                        css_class='form-group form-group-A row',
                    ),
                    Div(
                        HTML('<label class="col-md-4 control-label">Innate Stat</label>'),
                        Field('innate_stat', wrapper_class='col-md-4 inline-horizontal'),
                        Field('innate_stat_value', wrapper_class='col-md-4 inline-horizontal', placeholder='Value'),
                        css_class='form-group form-group-condensed row',
                    ),
                    Div(
                        Field('substats', wrapper_class='col-sm-3'),
                        Field('substat_values', wrapper_class='col-sm-3'),
                        Field('substats_enchanted', css_class='form-checkbox', wrapper_class='col-sm-3'),
                        Field('substats_grind_value', wrapper_class='col-sm-3'),
                        css_class='row'
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Assign To</label>'),
                        Div(
                            Field('assigned_to', wrapper_class='col-md-12', data_placeholder='Start typing...'),
                        ),
                        css_class='form-group form-group-condensed row',
                    ),
                    Div(
                        HTML('<label class="col-md-2 control-label">Notes</label>'),
                        Div(
                            Field('notes', rows="4", wrapper_class='col-md-10'),
                            Field('marked_for_sale'),
                        ),
                        css_class='form-group form-group-condensed row',
                    ),
                    css_class='form-horizontal',
                ),
                css_class='col-md-9',
            ),
            FormActions(
                Submit('save', 'Save', css_class='float-right'),
                css_class='col-12',
            ),
        )

    def clean_substats_grind_value(self):
        # Replace instances of None with 0
        return [x or 0 for x in self.cleaned_data['substats_grind_value']]


class AssignRuneForm(forms.Form):
    type = forms.MultipleChoiceField(
        choices=(('2-slot', '2-Slot Sets'), ('4-slot', '4-Slot Sets')) + RuneInstance.TYPE_CHOICES,
        required=False,
    )
    main_stat = forms.MultipleChoiceField(
        choices=RuneInstance.STAT_CHOICES,
        required=False,
    )
    innate_stat = forms.MultipleChoiceField(
        choices=RuneInstance.STAT_CHOICES,
        required=False,
    )
    substats = forms.MultipleChoiceField(
        label='Substats',
        choices=RuneInstance.STAT_CHOICES,
        required=False,
    )
    substat_logic = forms.BooleanField(
        label=mark_safe('<i class="fas fa-info-circle" data-bs-toggle="tooltip" title="Whether a rune must contain ALL substats or at least one of the filtered substats."></i>'),
        required=False,
    )
    level = forms.CharField(
        label='Level',
        required=False,
    )
    stars = forms.CharField(
        label='Stars',
        required=False
    )
    slot = forms.MultipleChoiceField(
        choices=((1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)),
        required=False,
    )
    quality = forms.MultipleChoiceField(
        choices=RuneInstance.QUALITY_CHOICES,
        required=False,
    )
    original_quality = forms.MultipleChoiceField(
        choices=RuneInstance.QUALITY_CHOICES,
        required=False,
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'AssignRuneForm'
    helper.layout = Layout(
        FormActions(
            StrictButton('Create New', id='addNewRune', css_class='btn btn-primary btn-block'),
            Reset('Reset Form', 'Reset Filters', css_class='btn btn-danger btn-block'),
        ),
        Field('type', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('quality', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('original_quality', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Div(
            Field(
                'level',
                data_provide='slider',
                data_slider_min='0',
                data_slider_max='15',
                data_slider_value='[0, 15]',
                data_slider_step='1',
                data_slider_ticks='[0, 15]',
                data_slider_ticks_labels='["0", "15"]',
                css_class='auto-submit',
                wrapper_class='form-group-sm form-group-condensed col-sm-6'
            ),
            Field(
                'stars',
                data_provide='slider',
                data_slider_min='1',
                data_slider_max='6',
                data_slider_value='[1, 6]',
                data_slider_step='1',
                data_slider_ticks='[1, 6]',
                data_slider_ticks_labels='["1", "6"]',
                css_class='auto-submit',
                wrapper_class='form-group-sm form-group-condensed col-sm-6'
            ),
            css_class='row'
        ),
        Field('main_stat', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),

        Field('innate_stat', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('substats', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('substat_logic', data_bs_toggle='toggle', data_on='One or More', data_onstyle='dark', data_off='All', data_width='125px', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed ps-0'),
        Field('slot', wrapper_class='visually-hidden'),
    )

    def clean(self):
        super(AssignRuneForm, self).clean()

        # Process x-slot shortcuts for rune set
        if '2-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('2-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.items():
                if count == 2:
                    self.cleaned_data['type'].append(rune_set)

        if '4-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('4-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.items():
                if count == 4:
                    self.cleaned_data['type'].append(rune_set)

        # Split the slider ranges into two min/max fields for the filters
        try:
            [min_lv, max_lv] = self.cleaned_data['level'].split(',')
        except:
            min_lv = 0
            max_lv = 15

        self.cleaned_data['level__gte'] = int(min_lv)
        self.cleaned_data['level__lte'] = int(max_lv)

        try:
            [min_stars, max_stars] = self.cleaned_data['stars'].split(',')
        except:
            min_stars = 1
            max_stars = 6

        self.cleaned_data['stars__gte'] = int(min_stars)
        self.cleaned_data['stars__lte'] = int(max_stars)


class FilterRuneForm(forms.Form):
    type = forms.MultipleChoiceField(
        choices=(('2-slot', '2-Slot Sets'), ('4-slot', '4-Slot Sets')) + RuneInstance.TYPE_CHOICES,
        required=False,
    )
    main_stat = forms.MultipleChoiceField(
        choices=RuneInstance.STAT_CHOICES,
        required=False,
    )
    innate_stat = forms.MultipleChoiceField(
        choices=RuneInstance.STAT_CHOICES,
        required=False,
    )
    substats = forms.MultipleChoiceField(
        label='Substats',
        choices=RuneInstance.STAT_CHOICES,
        required=False,
    )
    substat_logic = forms.BooleanField(
        label=mark_safe('<span class="glyphicon glyphicon-info-sign" data-bs-toggle="tooltip" title="Whether a rune must contain ALL substats or at least one of the filtered substats."></span>'),
        required=False,
    )
    substat_reverse = forms.BooleanField(
        label=mark_safe('<span class="glyphicon glyphicon-info-sign" data-bs-toggle="tooltip" title="If substats filters should be excluded."></span>'),
        required=False,
    )
    has_gem = forms.NullBooleanField(
        label='Enchant Gem Applied',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    has_grind = forms.CharField(
        label='Grinds Applied',
        required=False,
    )
    level = forms.CharField(
        label='Level',
        required=False,
    )
    stars = forms.CharField(
        label='Stars',
        required=False
    )
    slot = forms.MultipleChoiceField(
        choices=(('even', 'Even'), ('odd', 'Odd'), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6)),
        required=False,
    )
    quality = forms.MultipleChoiceField(
        choices=RuneInstance.QUALITY_CHOICES,
        required=False,
    )
    original_quality = forms.MultipleChoiceField(
        choices=RuneInstance.QUALITY_CHOICES,
        required=False,
    )
    ancient = forms.NullBooleanField(
        label='Ancient',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    assigned_to = forms.NullBooleanField(
        label='Is Assigned',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    marked_for_sale = forms.NullBooleanField(
        label='Marked for Sale',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No'))),
    )
    is_grindable = forms.NullBooleanField(
        label='Is Grindable',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    is_enchantable = forms.NullBooleanField(
        label='Is Enchantable',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )

    helper = FormHelper()
    helper.form_method = 'get'
    helper.form_id = 'FilterInventoryForm'
    helper.layout = Layout(
        Div(
            Div(
                Field('type', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('slot', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field(
                    'level',
                    data_provide='slider',
                    data_slider_min='0',
                    data_slider_max='15',
                    data_slider_value='[0, 15]',
                    data_slider_step='1',
                    data_slider_ticks='[0, 15]',
                    data_slider_ticks_labels='["0", "15"]',
                    wrapper_class='form-group-sm form-group-condensed'
                ),
                Field(
                    'stars',
                    data_provide='slider',
                    data_slider_min='1',
                    data_slider_max='6',
                    data_slider_value='[1, 6]',
                    data_slider_step='1',
                    data_slider_ticks='[1, 6]',
                    data_slider_ticks_labels='["1", "6"]',
                    wrapper_class='form-group-sm form-group-condensed'
                ),
                css_class='col-md-4 col-sm-6',
            ),
            Div(
                Field('main_stat', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('innate_stat', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('substats', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Div(
                    Field(
                        'substat_logic',
                        data_toggle='toggle',
                        data_on='One or More',
                        data_onstyle='dark',
                        data_off='All',
                        data_width='125px',
                        wrapper_class='form-group-sm form-group-condensed ps-0',
                    ), 
                    Field(
                        'substat_reverse',
                        data_toggle='toggle',
                        data_on='Exclude',
                        data_onstyle='dark',
                        data_off='Include',
                        data_width='125px',
                        wrapper_class='form-group-sm form-group-condensed',
                    ),
                    css_class='d-flex justify-content-between',
                ),
                Field(
                    'has_grind',
                    data_provide='slider',
                    data_slider_min='0',
                    data_slider_max='4',
                    data_slider_value='[0, 4]',
                    data_slider_step='1',
                    data_slider_ticks='[0, 4]',
                    data_slider_ticks_labels='["0", "4"]',
                    wrapper_class='form-group-sm form-group-condensed'
                ),
                Field('is_grindable', wrapper_class='form-group-sm form-group-condensed'),
                Field('is_enchantable', wrapper_class='form-group-sm form-group-condensed'),
                css_class='col-md-4 col-sm-6'
            ),
            Div(
                Field('quality', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('original_quality', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('ancient', wrapper_class='form-group-sm form-group-condensed'),
                Field('has_gem', wrapper_class='form-group-sm form-group-condensed'),
                Field('assigned_to', wrapper_class='form-group-sm form-group-condensed'),
                Field('marked_for_sale', wrapper_class='form-group-sm form-group-condensed'),
                css_class='col-md-4 col-sm-6'
            ),
            css_class='row',
        ),
        Div(
            Div(
                Submit('apply', 'Apply', css_class='btn-success '),
                css_class='btn-group w-50'
            ),
            Div(
                Button('resetBtn', 'Reset Filters', css_class='btn-outline-danger reset'),
                css_class='btn-group w-50'
            ),
            css_class='btn-group w-100'
        ),
    )

    def clean(self):
        super(FilterRuneForm, self).clean()

        # Process x-slot shortcuts for rune set
        if '2-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('2-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.items():
                if count == 2:
                    self.cleaned_data['type'].append(rune_set)

        if '4-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('4-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.items():
                if count == 4:
                    self.cleaned_data['type'].append(rune_set)

        # Split the slider ranges into two min/max fields for the filters
        try:
            [min_lv, max_lv] = self.cleaned_data['level'].split(',')
        except:
            min_lv = 0
            max_lv = 15

        self.cleaned_data['level__gte'] = int(min_lv)
        self.cleaned_data['level__lte'] = int(max_lv)

        try:
            [min_stars, max_stars] = self.cleaned_data['stars'].split(',')
        except:
            min_stars = 1
            max_stars = 6

        self.cleaned_data['stars__gte'] = int(min_stars)
        self.cleaned_data['stars__lte'] = int(max_stars)

        try:
            [min_grinds, max_grinds] = self.cleaned_data['has_grind'].split(',')
        except:
            min_grinds = 0
            max_grinds = 4

        self.cleaned_data['has_grind__gte'] = int(min_grinds)
        self.cleaned_data['has_grind__lte'] = int(max_grinds)

        # Process even/odd slot shortcuts for rune slot
        if 'even' in self.cleaned_data['slot']:
            self.cleaned_data['slot'].remove('even')
            self.cleaned_data['slot'] += [2, 4, 6]

        if 'odd' in self.cleaned_data['slot']:
            self.cleaned_data['slot'].remove('odd')
            self.cleaned_data['slot'] += [1, 3, 5]


class AddRuneCraftInstanceForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(AddRuneCraftInstanceForm, self).__init__(*args, **kwargs)
        self.fields['rune'].choices = self.fields['rune'].choices[1:]  # Remove the empty '----' option from the list
        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'addRuneCraftForm'
        self.helper.form_class = 'ajax-form'
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('rune', template="crispy/rune_button_radio_select.html"),
                    css_class='col-md-5',
                ),
                Div(
                    Field('type'),
                    Field('stat'),
                    Field('quality'),
                    Field('quantity'),
                    css_class='col-md-7',
                ),
                css_class='row'
            ),
            FormActions(
                Submit('save', 'Save', css_class='float-right'),
            ),
        )

    class Meta:
        model = RuneCraftInstance
        fields = (
            'type',
            'rune',
            'stat',
            'quality',
            'quantity',
        )


# Artifact forms
class ArtifactInstanceForm(ModelForm):
    effects = SplitArrayField(
        forms.TypedChoiceField(
            choices=((None, '---------'), ) + ArtifactInstance.EFFECT_CHOICES,
            coerce=int,
            empty_value=None,
        ),
        size=4,
        remove_trailing_nulls=True,
        label='Effect',
        required=False,
    )

    effects_value = SplitArrayField(
        forms.FloatField(required=False),
        size=4,
        remove_trailing_nulls=True,
        label='Value',
        required=False,
    )

    class Meta:
        model = ArtifactInstance
        fields = (
            'level', 'slot', 'element', 'archetype', 'original_quality',
            'main_stat',
            'effects', 'effects_value',
            'assigned_to',
        )
        widgets = {
            'assigned_to': autocomplete.ModelSelect2(url='monster-instance-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'addArtifactForm'
        self.helper.form_class = 'ajax-form'
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Field('slot', wrapper_class='col-md-4 inline-horizontal'),
                    Field('element', wrapper_class='col-md-4 inline-horizontal visually-hidden'),
                    Field('archetype', wrapper_class='col-md-4 inline-horizontal visually-hidden'),
                    Field('original_quality', wrapper_class='col-md-4 inline-horizontal'),
                    css_class='row'
                ),
                Div(
                    Field('main_stat', wrapper_class='col-md-4 inline-horizontal'),
                    Field('level', placeholder='0-15', min=0, max=15, wrapper_class='col-md-4 inline-horizontal'),
                    css_class='row',
                ),
                Div(
                    Field('effects', wrapper_class='col-sm-6'),
                    Field('effects_value', wrapper_class='col-sm-6'),
                    css_class='row'
                ),
                Div(
                    Field('assigned_to', wrapper_class='col-md-4', data_placeholder='Start typing...'),
                    css_class='row',
                ),
            ),
            Div(css_class='clearfix'),
            FormActions(
                Submit('save', 'Save', css_class='float-right'),
            ),
        )


class FilterArtifactForm(forms.Form):
    slot = forms.MultipleChoiceField(
        choices=ArtifactInstance.NORMAL_ELEMENT_CHOICES + ArtifactInstance.ARCHETYPE_CHOICES,
        required=False,
    )
    level = forms.CharField(
        label='Level',
        required=False,
    )
    quality = forms.MultipleChoiceField(
        choices=ArtifactInstance.QUALITY_CHOICES,
        required=False,
    )
    original_quality = forms.MultipleChoiceField(
        choices=ArtifactInstance.QUALITY_CHOICES,
        required=False,
    )
    assigned = forms.NullBooleanField(
        label='Is Assigned',
        required=False,
        widget=forms.Select(choices=((None, '---'), (True, 'Yes'), (False, 'No')))
    )
    main_stat = forms.MultipleChoiceField(
        choices=ArtifactInstance.MAIN_STAT_CHOICES,
        required=False,
    )
    effects = forms.MultipleChoiceField(
        label='Effects',
        choices=ArtifactInstance.EFFECT_CHOICES,
        required=False,
    )
    effects_logic = forms.BooleanField(
        label=mark_safe('<i class="fas fa-info-circle" data-bs-toggle="tooltip" title="Whether an artifact must contain ALL effects or at least one."></i>'),
        required=False,
    )

    helper = FormHelper()
    helper.form_method = 'get'
    helper.form_id = 'FilterInventoryForm'
    helper.layout = Layout(
        Div(
            Div(
                Field('slot', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field(
                    'level',
                    data_provide='slider',
                    data_slider_min='0',
                    data_slider_max='15',
                    data_slider_value='[0, 15]',
                    data_slider_step='1',
                    data_slider_ticks='[0, 15]',
                    data_slider_ticks_labels='["0", "15"]',
                    wrapper_class='form-group-sm form-group-condensed'
                ),
                css_class='col-md-4 col-sm-6',
            ),
            Div(
                Field('quality', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('original_quality', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('assigned', wrapper_class='form-group-sm form-group-condensed'),
                css_class='col-md-4 col-sm-6'
            ),
            Div(
                Field('main_stat', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field('effects', css_class='select2', wrapper_class='form-group-sm form-group-condensed'),
                Field(
                    'effects_logic',
                    data_toggle='toggle',
                    data_on='One or More',
                    data_onstyle='dark',
                    data_off='All',
                    data_width='125px',
                    wrapper_class='form-group-sm form-group-condensed ps-0',
                ),

                css_class='col-md-4 col-sm-6'
            ),
            css_class='row',
        ),
        Div(
            Div(
                Submit('apply', 'Apply', css_class='btn-success '),
                css_class='btn-group w-50'
            ),
            Div(
                Button('resetBtn', 'Reset Filters', css_class='btn-outline-danger reset'),
                css_class='btn-group w-50'
            ),
            css_class='btn-group w-100'
        ),
    )

    def clean(self):
        super().clean()

        # Split the slider ranges into two min/max fields for the filters
        try:
            [min_lv, max_lv] = self.cleaned_data['level'].split(',')
        except:
            min_lv = 0
            max_lv = 15

        self.cleaned_data['level__gte'] = int(min_lv)
        self.cleaned_data['level__lte'] = int(max_lv)


class AssignArtifactForm(forms.Form):
    slot = forms.MultipleChoiceField(
        choices=ArtifactInstance.NORMAL_ELEMENT_CHOICES + ArtifactInstance.ARCHETYPE_CHOICES,
        required=False,
    )
    level = forms.CharField(
        label='Level',
        required=False,
    )
    quality = forms.MultipleChoiceField(
        choices=ArtifactInstance.QUALITY_CHOICES,
        required=False,
    )
    original_quality = forms.MultipleChoiceField(
        choices=ArtifactInstance.QUALITY_CHOICES,
        required=False,
    )
    main_stat = forms.MultipleChoiceField(
        choices=ArtifactInstance.MAIN_STAT_CHOICES,
        required=False,
    )
    effects = forms.MultipleChoiceField(
        label='Effects',
        choices=ArtifactInstance.EFFECT_CHOICES,
        required=False,
    )
    effects_logic = forms.BooleanField(
        label=mark_safe(
            '<i class="fas fa-info-circle" data-bs-toggle="tooltip" title="Whether an artifact must contain ALL effects or at least one."></i>'),
        required=False,
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'AssignArtifactForm'
    helper.layout = Layout(
        FormActions(
            StrictButton('Create New', id='addNewArtifact', css_class='btn btn-primary btn-block'),
            Reset('Reset Form', 'Reset Filters', css_class='btn btn-danger btn-block'),
        ),
        Field('quality', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('original_quality', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field(
            'level',
            data_provide='slider',
            data_slider_min='0',
            data_slider_max='15',
            data_slider_value='[0, 15]',
            data_slider_step='1',
            data_slider_ticks='[0, 15]',
            data_slider_ticks_labels='["0", "15"]',
            css_class='auto-submit',
            wrapper_class='form-group-sm form-group-condensed'
        ),
        Field('main_stat', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('effects', css_class='select2 auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('effects_logic', data_bs_toggle='toggle', data_on='One or More', data_onstyle='dark', data_off='All', data_width='125px', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed ps-0'),
        Field('slot', wrapper_class='visually-hidden'),
    )

    def clean(self):
        super().clean()

        # Split the slider ranges into two min/max fields for the filters
        try:
            [min_lv, max_lv] = self.cleaned_data['level'].split(',')
        except:
            min_lv = 0
            max_lv = 15

        self.cleaned_data['level__gte'] = int(min_lv)
        self.cleaned_data['level__lte'] = int(max_lv)


# Profile import/export
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
    except_fusion_ingredient = forms.BooleanField(
        required=False,
        label='Import anyway if monster is fusion ingredient',
        initial=True,
    )
    lock_monsters = forms.BooleanField(
        required=False,
        label=mark_safe('<span class="glyphicon glyphicon-lock"></span> Copy locked status of monsters from in-game'),
        help_text='Locking on SWARFARM means a monster will not be used as fusion ingredients or skill-ups.',
        initial=True,
    )
    ignore_validation = forms.BooleanField(
        required=False,
        label='Ignore validation checks',
        initial=False,
    )
    save_defaults = forms.BooleanField(
        required=False,
        label='Save options as default',
        initial=False
    )


class MonsterImportOptionsLayout(Layout):
    def __init__(self):
        super(MonsterImportOptionsLayout, self).__init__(
            Div(
                HTML("""<h4 class="list-group-item-heading">Monster Filters</h4>"""),
                HTML("""<p class="text-warning">Note: If a monster is filtered out, it's equipped runes will not be imported either!</p>"""),
                Field('minimum_stars', template='crispy/button_radio_select.html'),
                Field('ignore_silver'),
                Field('ignore_material'),
                Field('except_with_runes'),
                Field('except_light_and_dark'),
                Field('except_fusion_ingredient'),
                css_class='list-group-item',
            ),
            Div(
                HTML("""<h4 class="list-group-item-heading">Import Options</h4>"""),
                Field('default_priority'),
                Field('lock_monsters'),
                Field('missing_monster_action'),
                Field('missing_rune_action'),
                Div(
                    Field('ignore_validation'),
                    css_class='callout callout-warning',
                ),
                Div(
                    Field('clear_profile'),
                    css_class='callout callout-danger',
                ),
                Field('save_defaults'),
                css_class='list-group-item',
            ),
        )


class ImportSWParserJSONForm(MonsterImportOptionsMixin, forms.Form):
    json_file = forms.FileField(
        required=True,
        label="Summoner's War JSON File",
    )

    helper = FormHelper()
    helper.form_class = 'import-form'
    helper.layout = Layout(
        Div(
            Div(
                Field('json_file', template='crispy/file_upload.html', css_class='form-control'),
                css_class='list-group-item',
            ),
            MonsterImportOptionsLayout(),
            Div(
                FormActions(
                    Submit('import', 'Import', css_class='float-right'),
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


# Data logs
class FilterLogTimeRangeMixin(forms.Form):
    timestamp__gte = forms.DateTimeField(
        label='Start Time',
        required=False,
    )
    timestamp__lte = forms.DateTimeField(
        label='End Time',
        required=False,
    )


class FilterLogTimeRangeLayout(Layout):
    def __init__(self):
        super().__init__(
            Fieldset(
                'Log Time Span',
                Field('timestamp__gte', autocomplete='off'),
                Field('timestamp__lte', autocomplete='off'),
            ),
        )


class FilterLogTimestamp(FilterLogTimeRangeMixin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        # self.helper.form_class = 'ajax-form'
        self.helper.form_id = 'id_FilterDungeonLogForm'
        self.helper.include_media = False
        self.helper.layout = Layout(
            FilterLogTimeRangeLayout(),
            Submit('submit', 'Apply')
        )


class FilterDungeonLogForm(FilterLogTimeRangeMixin):
    level__dungeon__in = forms.ModelMultipleChoiceField(
        label='Specific Dungeon',
        queryset=Dungeon.objects.filter(category__in=[
            Dungeon.CATEGORY_SCENARIO,
            Dungeon.CATEGORY_CAIROS,
            Dungeon.CATEGORY_DIMENSIONAL_HOLE,
            Dungeon.CATEGORY_SECRET,
        ], enabled=True),
        required=False,
    )
    level__dungeon__category__in = forms.MultipleChoiceField(
        choices=Dungeon.CATEGORY_CHOICES,
        label='Category',
        required=False
    )
    level__floor = forms.ChoiceField(
        label='Floor',
        choices=[(None, '---')] + [(floor, f'B{floor}') for floor in range(1, 11)],
        required=False,
    )
    level__difficulty__in = forms.MultipleChoiceField(
        choices=Level.DIFFICULTY_CHOICES,
        label='Difficulty (Scenario Only)',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Dungeon Filters',
                        Div(
                            Field('level__dungeon__in', css_class='select2', wrapper_class='col-md-6'),
                            Field('level__dungeon__category__in', css_class='select2', wrapper_class='col-md-6'),
                            css_class='row',
                        ),
                        Div(
                            Field('level__floor', wrapper_class='col-md-6'),
                            Field('level__difficulty__in', css_class='select2', wrapper_class='col-md-6'),
                            css_class='row',
                        )

                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


class FilterRiftDungeonForm(FilterLogTimeRangeMixin):
    grade__in = forms.MultipleChoiceField(
        label='Grade',
        choices=RiftDungeonLog.GRADE_CHOICES,
        required=False,
    )

    level__dungeon__in = forms.ModelMultipleChoiceField(
        label='Dungeon',
        queryset=Dungeon.objects.filter(category=Dungeon.CATEGORY_RIFT_OF_WORLDS_BEASTS),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Rift Beast Filters',
                        Field('level__dungeon__in', css_class='select2'),
                        Field('grade__in', css_class='select2'),
                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


class FilterRiftDungeonFormGradeOnly(FilterLogTimeRangeMixin):
    grade__in = forms.MultipleChoiceField(
        label='Grade',
        choices=RiftDungeonLog.GRADE_CHOICES,
        required=False,
    )

    level__dungeon__in = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Rift Beast Filters',
                        Field('grade__in', css_class='select2'),
                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


class FilterRiftRaidLogForm(FilterLogTimeRangeMixin):
    level__floor = forms.ChoiceField(
        label='Floor',
        choices=[(None, '---')] + [(floor, f'R{floor}') for floor in range(1, 6)],
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Dungeon Filters',
                        Field('level__floor'),
                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


class FilterWorldBossLogForm(FilterLogTimeRangeMixin):
    grade__in = forms.MultipleChoiceField(
        label='Grade',
        choices=WorldBossLog.GRADE_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'World Boss Filters',
                        Field('grade__in', css_class='select2'),
                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


class FilterSummonLogForm(FilterLogTimeRangeMixin):
    item__in = forms.ModelMultipleChoiceField(
        label='Method',
        queryset=GameItem.objects.all(),
        widget=autocomplete.ModelSelect2Multiple(
            url='summon-game-item-autocomplete',
        ),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Summon Filters',
                        Field('item__in'),
                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


class FilterRuneCraftLogForm(FilterLogTimeRangeMixin):
    craft_level__in = forms.MultipleChoiceField(
        label='Craft Level',
        choices=CraftRuneLog.CRAFT_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Rune Craft Filters',
                        Field('craft_level__in', css_class='select2'),
                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


class FilterMagicBoxCraftLogForm(FilterLogTimeRangeMixin):
    box_type__in = forms.MultipleChoiceField(
        label='Box Type',
        choices=MagicBoxCraft.BOX_CHOICES,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    Fieldset(
                        'Magic Box Craft Filters',
                        Field('box_type__in', css_class='select2'),
                    ),
                    css_class='col-md-6 col-xs-12'
                ),
                Div(
                    FilterLogTimeRangeLayout(),
                    css_class='col-md-6 col-xs-12'
                ),
                css_class='row',
            ),
            Submit('submit', 'Apply')
        )


# Compare
class CompareMonstersForm(forms.Form):
    monster_first = forms.ModelChoiceField(required=True, queryset=MonsterInstance.objects.all(), widget=autocomplete.ModelSelect2(url='monster-instance-autocomplete'))
    monster_second = forms.ModelChoiceField(required=True, queryset=MonsterInstance.objects.all(), widget=autocomplete.ModelSelect2(url='monster-instance-autocomplete'))

    def __init__(self, *args, **kwargs):
        super(CompareMonstersForm, self).__init__(*args, **kwargs)

        self.fields['monster_first'].label = False
        self.fields['monster_second'].label = False

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'compareMonstersForm'
        self.helper.form_class = 'form'
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML(f'<label class="control-label">First Monster</label>'),
                    Div(
                        Field('monster_first', wrapper_class='col-md-12', data_placeholder='Start typing...'),
                    ),
                    css_class='form-group form-group-condensed',
                ),
                Div(
                    HTML(f'<label class="control-label">Second Monster</label>'),
                    Div(
                        Field('monster_second', wrapper_class='col-md-12', data_placeholder='Start typing...'),
                    ),
                    css_class='form-group form-group-condensed',
                ),
                css_class='form-horizontal',
            ),
            Div(css_class='clearfix'),
            FormActions(
                Submit('save', 'Compare', css_class='float-right mr-15'),
            ),
        )

    def clean(self):
        super().clean()


class CompareMonstersWithFollowerForm(forms.Form):
    summoner_monster = forms.ModelChoiceField(required=True, queryset=MonsterInstance.objects.all(), widget=autocomplete.ModelSelect2(url='monster-instance-autocomplete'))
    follower_monster = forms.ModelChoiceField(required=True, queryset=MonsterInstance.objects.all(), widget=autocomplete.ModelSelect2(url='monster-instance-follower-autocomplete', forward=['follower_name']))
    follower_name = forms.CharField(required=True, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        summoner_name = kwargs.pop('summoner_name', None)
        follower_name = kwargs.pop('follower_name', None)
        super(CompareMonstersWithFollowerForm, self).__init__(*args, **kwargs)

        if follower_name:
            self.fields['follower_name'].initial = follower_name

        summoner_label = f"{summoner_name}'s Monster" if summoner_name else 'Your Monster'
        follower_label = f"{follower_name}'s Monster" if follower_name else 'Follower\'s Monster'

        self.fields['summoner_monster'].label = False
        self.fields['follower_monster'].label = False
        self.fields['follower_name'].label = False

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_id = 'compareMonstersWithFollowerForm'
        self.helper.form_class = 'ajax-form'
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Div(
                    HTML(f'<label class="control-label">{summoner_label}</label>'),
                    Div(
                        Field('summoner_monster', wrapper_class='col-md-12', data_placeholder='Start typing...'),
                    ),
                    css_class='form-group form-group-condensed',
                ),
                Div(
                    HTML(f'<label class="control-label">{follower_label}</label>'),
                    Div(
                        Field('follower_monster', wrapper_class='col-md-12', data_placeholder='Start typing...'),
                    ),
                    css_class='form-group form-group-condensed',
                ),
                css_class='form-horizontal',
            ),
            Div(
                Field('follower_name'),
            ),
            Div(css_class='clearfix'),
            FormActions(
                Submit('save', 'Compare', css_class='float-right mr-15'),
            ),
        )

    def clean(self):
        super().clean()
        