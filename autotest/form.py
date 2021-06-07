from django import forms


class ExecutionForm(forms.Form):
    # error_message并未使用
    func = forms.CharField(max_length=64, required=True, error_messages={'required': '节点注册方法和测试方法不能为空'})
    mthd = forms.CharField(max_length=64, required=True, error_messages={'required': '节点注册方法和测试方法不能为空'})
    ds_range = forms.CharField(max_length=64, required=False, initial=None)
    node = forms.CharField(max_length=32, required=False, initial=None)
    comment = forms.CharField(max_length=256, required=False, initial=None)


class DataSourceForm(forms.Form):
    ds_name = forms.CharField(max_length=64)
    file = forms.FileField(allow_empty_file=False)






