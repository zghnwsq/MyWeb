from django.db import models
from MyWeb import settings
# Create your models here.


class RunHis(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.CharField(max_length=64, null=False)
    suite = models.CharField(max_length=64, null=False)
    case = models.CharField(max_length=128, null=False)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=200, null=True)
    tester = models.CharField(max_length=32)
    comment = models.CharField(max_length=200, null=True)
    report = models.CharField(max_length=200)
    result = models.CharField(max_length=1)
    create_time = models.DateTimeField(auto_created=False)
    update_time = models.DateTimeField(auto_created=False)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'run_his'


class ResDict(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    result = models.CharField(max_length=1, null=False)
    description = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'res_dict'


class SuiteCount(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.CharField(max_length=32, null=True)
    suite = models.CharField(max_length=32, null=True)
    count = models.IntegerField(null=True)


class Node(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    ip_port = models.CharField(null=False, max_length=32)
    tag = models.CharField(max_length=64)
    status = models.CharField(max_length=16, default='on')

    def __str__(self):
        return self.ip_port


class RegisterFunction(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.CharField(max_length=32, null=True)
    suite = models.CharField(max_length=32, null=True)
    func = models.CharField(max_length=64, null=False)
    node = models.CharField(max_length=32, null=True)
    tests = models.CharField(max_length=512, null=True)


class Execution(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    func = models.ForeignKey(RegisterFunction, blank=False, null=False, on_delete=models.CASCADE, db_constraint=False)
    method = models.CharField(max_length=64)
    ds_range = models.CharField(max_length=32, null=True)
    comment = models.CharField(max_length=64, null=True)
    status = models.CharField(max_length=256, null=True)


class JobQueue(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    executioin = models.ForeignKey(Execution, on_delete=models.CASCADE, null=False, db_constraint=False)
    node = models.CharField(max_length=32, null=False)
    status = models.CharField(max_length=256, null=False)
    tester = models.CharField(max_length=32)
    create_time = models.DateTimeField(auto_created=True)
    update_time = models.DateTimeField(auto_created=False, null=True)


class DataSource(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    ds_name = models.CharField(max_length=64, null=False)
    file_name = models.CharField(max_length=128, null=False)
    file_path = models.FilePathField(path=settings.DATA_SOURCE_ROOT, max_length=256, null=False)
    update_time = models.DateTimeField(auto_created=False, null=True)




