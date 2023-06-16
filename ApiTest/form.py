from django import forms


class ApiAttachForm(forms.Form):
    case_id = forms.IntegerField(required=True)
    file = forms.FileField(allow_empty_file=False)


class CaseParamUploadForm(forms.Form):
    case_id = forms.IntegerField(required=True)
    sheetname = forms.CharField(max_length=256, required=False, empty_value=None)
    file = forms.FileField(allow_empty_file=False)



