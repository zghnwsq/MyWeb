"""
@Time ： 2023/4/8 11:23
@Auth ： Ted
@File ：serializers.py
@IDE ：PyCharm
"""
from django import forms
from Utils.JsonSerializerForm import JsonSerializerForm, ListFormField


class UpdateGroupSerializer(JsonSerializerForm):
    group_id = forms.IntegerField(required=True)
    group = forms.CharField(required=True, min_length=1, max_length=64)


class DeleteGroupSerializer(JsonSerializerForm):
    group_id = forms.IntegerField(required=True)


class NewGroupSerializer(JsonSerializerForm):
    group = forms.CharField(required=True, min_length=1, max_length=64)


class GroupEnvSerializer(JsonSerializerForm):
    id = forms.IntegerField(required=False)
    env_key = forms.CharField(required=True, max_length=256)
    env_value = forms.CharField(required=True, max_length=256)


class EditGroupEnvSerializer(JsonSerializerForm):
    group_id = forms.IntegerField(required=True)
    data = ListFormField(required=True, item_form=GroupEnvSerializer)


class DeleteEnvSerializer(JsonSerializerForm):
    env_id = forms.IntegerField(required=True)


class CaseSerializer(JsonSerializerForm):
    id = forms.IntegerField(required=True)
    suite = forms.CharField(max_length=64, required=False, empty_value='')
    title = forms.CharField(max_length=128, required=False, empty_value='')


class DeleteCaseSerializer(JsonSerializerForm):
    cases = ListFormField(required=True, item_form=CaseSerializer)


class NewCaseSerializer(JsonSerializerForm):
    group = forms.IntegerField(required=True)
    suite = forms.CharField(max_length=64, required=True)
    title = forms.CharField(max_length=128, required=True)


class CaseStepSerializer(JsonSerializerForm):
    id = forms.IntegerField(required=False)
    step_action = forms.CharField(required=True, max_length=128)
    step_p1 = forms.CharField(required=False, max_length=1024)
    step_p2 = forms.CharField(required=False, max_length=1024)
    step_p3 = forms.CharField(required=False, max_length=1024)
    title = forms.CharField(required=False, max_length=128)


class EditCaseSerializer(JsonSerializerForm):
    case_id = forms.IntegerField(required=True)
    data = ListFormField(required=True, item_form=CaseStepSerializer)


class DuplicateCasesSerializer(JsonSerializerForm):
    cases = ListFormField(required=True, item_form=CaseSerializer)


class CaseParamSerializer(JsonSerializerForm):
    id = forms.IntegerField(required=False)
    p_name = forms.CharField(required=True, min_length=1, max_length=256)
    desc = forms.CharField(required=False, max_length=256, empty_value='')


class EditCaseDsSerializer(JsonSerializerForm):
    case_id = forms.IntegerField(required=True)
    data = ListFormField(required=False, item_form=CaseParamSerializer)
    copy_case_id = forms.IntegerField(required=False)


class DeleteCaseParamSerializer(JsonSerializerForm):
    params = forms.JSONField(required=True)


class CaseParamValueSerializer(JsonSerializerForm):
    id = forms.IntegerField(required=False)
    p_value = forms.CharField(required=True, min_length=1, max_length=512)


class EditCaseDsValueSerializer(JsonSerializerForm):
    param_id = forms.IntegerField(required=True)
    data = ListFormField(required=True, item_form=CaseParamValueSerializer)


class DeleteCaseDsValueSerializer(JsonSerializerForm):
    values = forms.JSONField(required=True)


class ExecJobSerializer(JsonSerializerForm):
    cases = forms.JSONField(required=True)
    debug = forms.ChoiceField(choices=(('True', 'True'), ('False', 'False')), required=False)
    stop_after_fail = forms.ChoiceField(choices=(('True', 'True'), ('False', 'False')), required=False)

