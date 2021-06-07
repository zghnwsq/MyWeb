import os
import time
import uuid
from django.core.files.storage import FileSystemStorage
from MyWeb import settings
from autotest.models import DataSource


def update_datasource(ds_name, file):
    abs_path = os.path.join(settings.DATA_SOURCE_ROOT, ds_name)
    if not os.path.isdir(abs_path):
        os.makedirs(abs_path)
    storage = FileSystemStorage(location=abs_path)
    exist_files = DataSource.objects.filter(ds_name=ds_name)
    for exist_file in exist_files:
        if os.path.isfile(exist_file.file_path):
            os.remove(exist_file.file_path)
    now = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    u_file_name = str(uuid.uuid5(uuid.NAMESPACE_DNS, ds_name)).replace('-', '_')
    with storage.open(u_file_name, 'wb') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    if len(exist_files) > 0:
        exist_files.update(file_path=os.path.join(abs_path, u_file_name), update_time=now)
    else:
        DataSource(ds_name=ds_name, file_path=os.path.join(abs_path, u_file_name),
                   update_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())).save()

    return '数据源更新成功!'









