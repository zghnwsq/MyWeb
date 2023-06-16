"""
@Time ： 2023/4/7 17:18
@Auth ： Ted
@File ：JsonSerializerForm.py
@IDE ：PyCharm
"""
from django import forms


class InvalidFormException(Exception):
    pass


class JsonSerializerForm(forms.Form):
    """
        借用forms.Form类验证请求是否合规,不合规返回校验报错信息
    """

    def get_data(self) -> dict:
        """
            校验请求字典是否合法
        :return: dict
        """
        if self.is_valid():
            return {field: self.cleaned_data[field] for field in self.fields}
        else:
            msg = ','.join([f'{key}: {" ".join(self.errors[key])}' for key in self.errors.keys()])
            raise InvalidFormException(msg)


class ListFormField(forms.Field):
    def __init__(self, *args, **kwargs):
        self.item_form = kwargs.pop('item_form', forms.Form)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not isinstance(value, list):
            raise forms.ValidationError('Value must be a list')
        item_form = self.item_form
        result = []
        for item in value:
            f = item_form(item)
            if f.is_valid():
                result.append(f.cleaned_data)
            else:
                msg = ','.join([f'{key}: {" ".join(f.errors[key])}' for key in f.errors.keys()])
                raise forms.ValidationError(msg)
        return result

    def is_valid(self, value):
        try:
            self.to_python(value)
            return True
        except forms.ValidationError:
            return False


class SubFormField(forms.Field):
    def __init__(self, *args, **kwargs):
        self.item_form = kwargs.pop('item_form', forms.Form)
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        item_form = self.item_form
        f = item_form(value)
        if f.is_valid():
            return f.cleaned_data
        else:
            msg = ','.join([f'{key}: {" ".join(f.errors[key])}' for key in f.errors.keys()])
            raise forms.ValidationError(msg)

    def is_valid(self, value):
        try:
            self.to_python(value)
            return True
        except forms.ValidationError:
            return False

