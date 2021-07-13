from django import forms


class CaseForm(forms.Form):
    case_id = forms.IntegerField(required=True)
    suite = forms.CharField(max_length=64, required=False, empty_value='')
    title = forms.CharField(max_length=128, required=False, empty_value='')



