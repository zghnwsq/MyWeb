from django import forms
from django.forms import widgets


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, strip=True, required=True)
    password = forms.PasswordInput()


class PersonalInfoForm(forms.Form):
    email = forms.EmailField(max_length=64, required=True)


class ChangePasswordFrom(forms.Form):
    old_pwd = forms.CharField(widget=widgets.PasswordInput(), max_length=64, required=True)
    new_pwd = forms.CharField(widget=widgets.PasswordInput(), max_length=64, required=True)
    repeat_pwd = forms.CharField(widget=widgets.PasswordInput(), max_length=64, required=True)
