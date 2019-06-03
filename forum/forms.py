from django import forms
from django.forms.utils import ErrorList
from .models import Farmer, Question, Answer
from django.utils.translation import gettext as _


class PlainErrorList(ErrorList):
    """ Show errors as plain text, instead of unordered list """

    def __str__(self):
        return self.as_plain()

    def as_plain(self):
        if not self:
            return ''

        return '%s' % ''.join(['%s' % e for e in self])


class MaterialForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Show errors as plain text, instead of
        # unordered list
        self.error_class = PlainErrorList

        for field_name, field in self.fields.items():

            # if the field is a textarea field
            # then append `materialize-textarea` class to the field

            if isinstance(field.widget, forms.Textarea):

                OLD_CLASS = field.widget.attrs.get('class', "")
                NEW_CLASS = " materialize-textarea"

                field.widget.attrs.update({
                    'class': OLD_CLASS + NEW_CLASS
                })

    def add_error(self, field, error):

        super().add_error(field, error)

        for field_name, field in self.fields.items():
            if self[field_name].errors:

                OLD_CLASS = field.widget.attrs.get('class', "")
                NEW_CLASS = " invalid"

                field.widget.attrs.update(
                    {'class':  OLD_CLASS + NEW_CLASS})


class SignupForm(MaterialForm, forms.ModelForm):

    class Meta:
        model = Farmer
        fields = ['name', 'phone_number', 'password']

        widgets = {
            'phone_number': forms.TextInput(
                attrs={
                    'autofocus': False,
                    'type': 'tel'
                }
            ),
            'password': forms.PasswordInput(
                attrs={
                    'type': 'password'
                }
            ),
            'dob': forms.TextInput(
                attrs={
                    'placeholder': 'YYYY-MM-DD'
                }
            )
        }


class LoginForm(MaterialForm):

    phone_number = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'autofocus': False,
                'type': 'tel'
            }
        ), label=_("Phone number")
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                'type': 'password'
            }
        ), label=_("Farmer's password")
    )


class CreateQuestionForm(MaterialForm, forms.ModelForm):

    file_field = forms.FileField(required=False,
                                 widget=forms.FileInput(
                                     attrs={
                                         'multiple': True,
                                         'accept': 'image/*, video/*'
                                     }
                                 ))

    class Meta:
        model = Question
        fields = ['question', 'category']

        widgets = {
            'question': forms.Textarea(
                attrs={
                    'autofocus': True,
                    'value': ''
                }
            )
        }


class CreateAnswerForm(MaterialForm, forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['answer', ]

        widgets = {
            'answer': forms.Textarea(
                attrs={
                    'autofocus': True,
                    'value': ''
                }
            )
        }


class FarmerEditForm(MaterialForm, forms.ModelForm):

    class Meta:
        model = Farmer
        exclude = ['date_time_created', 'password']

        widgets = {
            'phone_number': forms.Textarea(
                attrs={
                    'autofocus': True
                }
            )
        }
