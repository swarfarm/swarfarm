from django.forms import ModelForm

from .models import Issue, Discussion

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field
from crispy_forms.bootstrap import FormActions, InlineField

from captcha.fields import ReCaptchaField


class IssueForm(ModelForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(IssueForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'feedback:issue_add'
        self.helper.layout = Layout(
            Div(
                Field('topic'),
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
        fields = ('topic', 'subject', 'description', 'public')
        labels = {
            'public': 'Allow other users to view and comment.',
        }


class IssueUpdateStatusForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(IssueUpdateStatusForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'feedback:issue_update'
        self.helper.form_class = 'form-inline'
        self.helper.layout = Layout(
            InlineField('status'),
            InlineField('priority'),
            FormActions(
                Submit('save', 'Save', css_class='btn btn-primary'),
            ),
        )

    class Meta:
        model = Issue
        fields = ('status', 'priority',)


class CommentForm(ModelForm):
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
