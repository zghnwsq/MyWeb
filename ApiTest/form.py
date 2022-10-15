from django import forms


class CaseForm(forms.Form):
    id = forms.IntegerField(required=True)
    suite = forms.CharField(max_length=64, required=False, empty_value='')
    title = forms.CharField(max_length=128, required=False, empty_value='')


class ApiAttachForm(forms.Form):
    case_id = forms.IntegerField(required=True)
    file = forms.FileField(allow_empty_file=False)


class CaseParamUploadForm(forms.Form):
    case_id = forms.IntegerField(required=True)
    sheetname = forms.CharField(max_length=256, required=False, empty_value=None)
    file = forms.FileField(allow_empty_file=False)




