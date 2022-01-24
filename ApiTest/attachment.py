"""
@Time ： 2022/1/20 15:10
@Auth ： Ted
@File ：attachment.py
@IDE ：PyCharm
"""
import os.path
import time
import uuid
from django.core.files.storage import FileSystemStorage
from ApiTest.models import ApiGroup, ApiCase, ApiAttachment
from MyWeb import settings


def save_attachment(case_id, file):
    case = ApiCase.objects.filter(id=case_id)
    if len(case) > 0:
        group = ApiGroup.objects.filter(id=case[0].group.id)
        if len(group) < 1:
            return '用例组不存在'
        group_name = group[0].group
        directory = os.path.join(settings.API_ATTACHMENT_ROOT, group_name)
        if not os.path.exists(directory):
            os.mkdir(directory)
        suffix = file.name.split('.')[1]
        file_name = file.name.split('.')[0]
        now = time.strftime('%Y-%m-%d_%H:%M:%S', time.localtime())
        uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f'{str(case_id)}{now}')).replace('-', '')
        file_path = os.path.join(group_name, f'{uid}.{suffix}')
        storage = FileSystemStorage(location=directory)
        with storage.open(f'{uid}.{suffix}', 'wb') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        ApiAttachment(group=group[0], file_name=file_name, uuid=uid, suffix=suffix, path=file_path).save()
        return '附件上传成功', {'uuid': uid, 'file_name': file_name, 'suffix': suffix}
    else:
        return '用例不存在'
