from django import forms
from django.forms import ModelForm
from django.forms.models import BaseModelFormSet
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from bestiary.models import Monster, Effect, LeaderSkill, ScalingStat
from bestiary.forms import effect_choices
from .models import MonsterInstance, MonsterTag, MonsterPiece, Summoner, TeamGroup, Team, RuneInstance, RuneCraftInstance, BuildingInstance

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML, Hidden, Reset, Fieldset
from crispy_forms.bootstrap import FormActions, PrependedText, FieldWithButtons, StrictButton, InlineField, InlineRadios, Alert

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
                Field('server'),
            ),
        )

    class Meta:
        model = Summoner
        fields = (
            'summoner_name',
            'public',
            'timezone',
            'server',
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


# Profile forms
class EditBuildingForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditBuildingForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_class = 'ajax-form'
        # self.helper.form_action must be set in view
        self.helper.layout = Layout(
            Field('level', autocomplete='off'),
            FormActions(
                Submit('save', 'Save', css_class='btn-success')
            )
        )

    class Meta:
        model = BuildingInstance
        fields = [
            'level',
        ]


# MonsterInstance Forms
class AddMonsterInstanceForm(autocomplete_light.ModelForm):
    monster = autocomplete_light.ModelChoiceField('MonsterAutocomplete')

    def __init__(self, *args, **kwargs):
        super(AddMonsterInstanceForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_class = 'ajax-form'
        self.helper.form_id = 'id_AddMonsterInstanceForm'
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
        labels = {
            'ignore_for_fusion': mark_safe('<span class="glyphicon glyphicon-lock"></span>Locked'),
        }


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
        labels = {
            'ignore_for_fusion': mark_safe('<span class="glyphicon glyphicon-lock"></span>Locked'),
        }
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
    monster__name = forms.CharField(
        label='Monster Name',
        max_length=100,
        required=False,
    )
    tags__pk = forms.MultipleChoiceField(
        label='Tags',
        choices=MonsterTag.objects.values_list('pk', 'name'),
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
    monster__element = forms.MultipleChoiceField(
        label='Element',
        choices=Monster.ELEMENT_CHOICES,
        required=False,
    )
    monster__archetype = forms.MultipleChoiceField(
        label='Archetype',
        choices=Monster.TYPE_CHOICES,
        required=False,
    )
    priority = forms.MultipleChoiceField(
        label='Priority',
        choices=MonsterInstance.PRIORITY_CHOICES,
        required=False,
    )
    monster__is_awakened = forms.ChoiceField(
        label='Awakened',
        required=False,
        choices=[(None, 'N/A'), (True, 'Yes'), (False, 'No')],
        widget=forms.RadioSelect,
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
    monster__skills__scaling_stats__pk = forms.MultipleChoiceField(
        label='Scales With',
        choices=ScalingStat.objects.values_list('pk', 'stat'),
        required=False,
    )
    buff_debuff_effects = forms.MultipleChoiceField(
        label='Buffs/Debuffs',
        choices=effect_choices(Effect.objects.exclude(icon_filename='')),
        required=False,
    )
    other_effects = forms.MultipleChoiceField(
        label='Other Effects',
        choices=Effect.other_effect_choices.all(),
        required=False,
    )
    effects_logic = forms.BooleanField(
        label=mark_safe('<span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" title="Whether all effect filters must be on ONE individual skill or can be spread across ANY skill in a monster\'s skill set."></span>'),
        required=False,
        initial=True,
    )

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'FilterInventoryForm'
    helper.layout = Layout(
        Div(
            Fieldset(
                'General',
                Div(
                    Div(
                        Field('monster__name', wrapper_class='form-group-sm form-group-condensed'),
                        Div(
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
                            Field('monster__element', css_class='select2-element', wrapper_class='form-group-sm form-group-condensed col-sm-6'),
                            css_class='row',
                        ),
                        css_class='col-lg-8 col-md-6'
                    ),
                    Div(
                        InlineRadios('monster__is_awakened', wrapper_class='form-group-sm form-group-condensed'),
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
                        Field('buff_debuff_effects', css_class='select2-effect', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field('other_effects', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field('monster__skills__scaling_stats__pk', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-lg-6'),
                        Field('effects_logic', data_toggle='toggle', data_on='Any Skill', data_onstyle='primary', data_off='One Skill', data_offstyle='primary', data_width='125px', wrapper_class='form-group-sm form-group-condensed col-lg-12'),
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
                css_class='btn-group'
            ),
            Div(
                Button('resetBtn', 'Reset Filters', css_class='btn-danger reset'),
                css_class='btn-group'
            ),
            css_class='btn-group btn-group-justified'
        ),
    )

    def clean(self):
        super(FilterMonsterInstanceForm, self).clean()

        # Coalesce the effect fields into a single one that the filter can understand
        buff_debuff_effects = self.cleaned_data.get('buff_debuff_effects')
        other_effects = self.cleaned_data.get('other_effects')
        self.cleaned_data['monster__skills__skill_effect__pk'] = buff_debuff_effects + other_effects

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

        # Split the slider ranges into two min/max fields for the filters
        try:
            [min_lv, max_lv] = self.cleaned_data['level'].split(',')
        except:
            min_lv = 1
            max_lv = 40

        self.cleaned_data['level__gte'] = int(min_lv)
        self.cleaned_data['level__lte'] = int(max_lv)

        try:
            [min_stars, max_stars] = self.cleaned_data['stars'].split(',')
        except:
            min_stars = 1
            max_stars = 6

        self.cleaned_data['stars__gte'] = int(min_stars)
        self.cleaned_data['stars__lte'] = int(max_stars)


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
        self.fields['notes'].label = False

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
                    Div(Field('slot', placeholder='1-6', min=1, max=6), css_class='col-md-3'),
                    Div(Field('stars', placeholder='1-6', min=1, max=6), css_class='col-md-4'),
                    Div(Field('level', placeholder='0-15', min=0, max=15), css_class='col-md-4'),
                    css_class='row'
                ),
                Div(
                    Div(
                        HTML('<label class="col-md-2 control-label">Main Stat</label>'),
                        Field('main_stat', wrapper_class='col-md-4 inline-horizontal'),
                        Field('main_stat_value', wrapper_class='col-md-3 inline-horizontal'),
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
                    Div(
                        HTML('<label class="col-md-2 control-label">Notes</label>'),
                        Div(
                            Field('notes', rows="4", wrapper_class='col-md-10'),
                            Field('marked_for_sale', wrapper_class='col-md-offset-2 col-md-10'),
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
            'assigned_to', 'notes', 'marked_for_sale',
        )
        widgets = {
            'assigned_to': autocomplete_light.ChoiceWidget('MonsterInstanceAutocomplete'),
        }


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
        label=mark_safe('<span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" title="Whether a rune must contain ALL substats or at least one of the filtered substats."></span>'),
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
        choices=((None, 'Unknown'),) + RuneInstance.QUALITY_CHOICES,
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
        Field('substat_logic', data_toggle='toggle', data_on='One or More', data_onstyle='primary', data_off='All', data_offstyle='primary', data_width='125px', css_class='auto-submit', wrapper_class='form-group-sm form-group-condensed'),
        Field('slot', type='hidden'),
    )

    def clean(self):
        super(AssignRuneForm, self).clean()

        # Process x-slot shortcuts for rune set
        if '2-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('2-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.iteritems():
                if count == 2:
                    self.cleaned_data['type'].append(rune_set)

        if '4-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('4-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.iteritems():
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
        label=mark_safe('<span class="glyphicon glyphicon-info-sign" data-toggle="tooltip" title="Whether a rune must contain ALL substats or at least one of the filtered substats."></span>'),
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
        choices=((None, 'Unknown'),) + RuneInstance.QUALITY_CHOICES,
        required=False,
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

    helper = FormHelper()
    helper.form_method = 'post'
    helper.form_id = 'FilterInventoryForm'
    helper.layout = Layout(
        Div(
            Field('type', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-4 col-sm-4'),
            Field('slot', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-4 col-sm-4'),
            Field('main_stat', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-4 col-sm-4'),
            Field(
                'stars',
                data_provide='slider',
                data_slider_min='1',
                data_slider_max='6',
                data_slider_value='[1, 6]',
                data_slider_step='1',
                data_slider_ticks='[1, 6]',
                data_slider_ticks_labels='["1", "6"]',
                wrapper_class='form-group-sm form-group-condensed col-md-4 col-sm-4'
            ),
            Field(
                'level',
                data_provide='slider',
                data_slider_min='0',
                data_slider_max='15',
                data_slider_value='[0, 15]',
                data_slider_step='1',
                data_slider_ticks='[0, 15]',
                data_slider_ticks_labels='["0", "15"]',
                wrapper_class='form-group-sm form-group-condensed col-md-4 col-sm-4'
            ),
            Field('innate_stat', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-4 col-sm-4'),
            Div(
                Field('substats', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-sm-12'),
                Field('substat_logic', data_toggle='toggle', data_on='One or More', data_onstyle='primary', data_off='All', data_offstyle='primary', data_width='125px', wrapper_class='form-group-sm form-group-condensed col-lg-12',),
                css_class='row col-md-4 col-sm-4'
            ),
            Field('quality', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-3 col-sm-3'),
            Field('original_quality', css_class='select2', wrapper_class='form-group-sm form-group-condensed col-md-3 col-sm-3'),
            Field('assigned_to', wrapper_class='form-group-sm form-group-condensed col-md-3 col-sm-3'),
            Field('marked_for_sale', wrapper_class='form-group-sm form-group-condensed col-md-3 col-sm-3'),
            css_class='row',
        ),
        Div(
            Div(
                Submit('apply', 'Apply', css_class='btn-success '),
                css_class='btn-group'
            ),
            Div(
                Button('resetBtn', 'Reset Filters', css_class='btn-danger reset'),
                css_class='btn-group'
            ),
            css_class='btn-group btn-group-justified'
        ),
    )

    def clean(self):
        super(FilterRuneForm, self).clean()

        # Process x-slot shortcuts for rune set
        if '2-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('2-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.iteritems():
                if count == 2:
                    self.cleaned_data['type'].append(rune_set)

        if '4-slot' in self.cleaned_data['type']:
            self.cleaned_data['type'].remove('4-slot')
            for rune_set, count in RuneInstance.RUNE_SET_COUNT_REQUIREMENTS.iteritems():
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

        # Process even/odd slot shortcuts for rune slot
        if 'even' in self.cleaned_data['slot']:
            self.cleaned_data['slot'].remove('even')
            self.cleaned_data['slot'] += [2, 4, 6]

        if 'odd' in self.cleaned_data['slot']:
            self.cleaned_data['slot'].remove('odd')
            self.cleaned_data['slot'] += [1, 3, 5]


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
                Field('rune', template="crispy/rune_button_radio_select.html"),
                css_class='col-md-4',
            ),
            Div(
                Field('type'),
                Field('stat'),
                Field('quality'),
                css_class='col-md-8',
            ),
            Div(css_class='clearfix'),
            FormActions(
                Submit('save', 'Save'),
            )
        )

    class Meta:
        model = RuneCraftInstance
        fields = (
            'type', 'rune', 'stat', 'quality'
        )
