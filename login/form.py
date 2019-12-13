from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, strip=True, required=True)
    password = forms.PasswordInput()
