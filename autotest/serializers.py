"""
@Time ： 2023/4/7 17:29
@Auth ： Ted
@File ：serializers.py
@IDE ：PyCharm
"""
from django import forms
from Utils.JsonSerializerForm import JsonSerializerForm


class UpdateRunhisCommentSerializer(JsonSerializerForm):
    group = forms.CharField(required=False)
    suite = forms.CharField(required=False)
    case = forms.CharField(required=False)
    title = forms.CharField(required=False)
    report = forms.CharField(required=False)
    comment = forms.CharField(required=False)
    create_time = forms.CharField(required=False)


class ExecutionSerializer(JsonSerializerForm):
    job_id = forms.IntegerField(required=False)
    func = forms.CharField(max_length=64, required=True, error_messages={'required': '节点注册方法和测试方法不能为空'})
    mthd = forms.CharField(max_length=64, required=True, error_messages={'required': '节点注册方法和测试方法不能为空'})
    ds_range = forms.CharField(max_length=64, required=False, empty_value='')
    node = forms.CharField(max_length=32, required=False, empty_value='')
    comment = forms.CharField(max_length=256, required=False, empty_value='')


class RegsiterNodeSerializer(JsonSerializerForm):
    type = forms.ChoiceField(choices=(('update', 'update'), ('node_off', 'node_off')))
    host_ip = forms.CharField(required=True)
    tag = forms.CharField(required=False, empty_value='')
    func = forms.JSONField(required=False, empty_value={})


class UpdateSuiteCaseCountSerializer(JsonSerializerForm):
    group_name = forms.CharField(required=True)
    test_suite = forms.CharField(required=True)
    case_count = forms.IntegerField(required=True)
