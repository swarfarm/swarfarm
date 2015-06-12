from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator

from .models import Feedback

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Div, Layout, Field, Button, HTML
from crispy_forms.bootstrap import FormActions

from captcha.fields import ReCaptchaField

class FeedbackForm(forms.ModelForm):
    captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        super(FeedbackForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper(self)
        self.helper.form_method = 'post'
        self.helper.form_action = 'feedback:index'
        self.helper.layout = Layout(
            Div(
                Field('topic'),
                Field('level'),
                Field('subject'),
                Field('feedback'),
                Field('captcha'),
            ),
            Div(
                FormActions(
                    Submit('save', 'Save', css_class='btn btn-primary'),
                ),
            )
        )

    class Meta:
        model = Feedback
        exclude = ('user', 'submitted',)
