from django import forms
from django.forms import ModelForm

from .models import MonsterInstance

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML
from crispy_forms.bootstrap import FormActions


class RegisterUserForm(forms.Form):
    username = forms.CharField(label='Username', required=True)
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

class EditEssenceStorageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EditEssenceStorageForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'herders:edit_essences'


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
                    HTML("""<a href="{% url 'herders:profile' %}" class="btn btn-link">Cancel</a>"""),
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
                HTML("""<a href="{% url 'herders:profile' %}" class="btn btn-link">Cancel</a>"""),
            ),
        )
    )
