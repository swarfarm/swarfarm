from django import forms

from .models import Issue, Discussion

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field
from crispy_forms.bootstrap import FormActions, FieldWithButtons

from captcha.fields import ReCaptchaField


class IssueForm(forms.ModelForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'feedback:issue_add'
        self.helper.layout = Layout(
            Div(
                Field('subject'),
                Field('description', data_provide='markdown'),
                Field('public'),
                Field('captcha'),
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                ),
            )
        )

    class Meta:
        model = Issue
        fields = ('subject', 'description', 'public')
        labels = {
            'public': 'Allow other users to view and comment.',
        }


class CommentForm(forms.ModelForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('comment', data_provide='markdown'),
            Field('captcha'),
            FormActions(
                Submit('save', 'Save', css_class='btn btn-primary'),
            ),
        )

    class Meta:
        model = Discussion
        fields = ('comment',)


class SearchForm(forms.Form):
    search = forms.CharField(
        label='Search',
        required=True
    )

    helper = FormHelper()
    helper.form_method = 'get'
    helper.form_show_labels = False
    helper.form_class = 'pull-right col-sm-3 col-md-4'
    helper.layout = Layout(
        FieldWithButtons(
            Field('search', placeholder='Search...'),
            Submit('', 'Search')
        ),
    )
