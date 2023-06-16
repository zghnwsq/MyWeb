from django import forms


class DataSourceForm(forms.Form):
    ds_name = forms.CharField(max_length=64)
    file = forms.FileField(allow_empty_file=False)






