from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ApiGroup(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.CharField(max_length=64, null=False)
    author = models.ForeignKey(User, null=False, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=1)

    def __str__(self):
        return self.group

    class Meta:
        db_table = 'api_group'


class ApiGroupEnv(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.ForeignKey(ApiGroup, null=False, on_delete=models.CASCADE)
    env_key = models.CharField(max_length=256, null=False, blank=False)
    env_value = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.env_key

    class Meta:
        db_table = 'api_group_env'


class ApiCase(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.ForeignKey(ApiGroup, null=False, on_delete=models.CASCADE)
    suite = models.CharField(max_length=64, null=False)
    title = models.CharField(max_length=128, null=False)
    author = models.ForeignKey(User, null=False, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_case'


class ApiCaseStep(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    case = models.ForeignKey(ApiCase, null=False, on_delete=models.CASCADE)
    step_action = models.CharField(max_length=128, null=False)
    step_p1 = models.CharField(max_length=1024, null=True)
    step_p2 = models.CharField(max_length=1024, null=True)
    step_p3 = models.CharField(max_length=1024, null=True)
    step_order = models.IntegerField(null=False, blank=False)
    title = models.CharField(max_length=128, null=True)

    def __str__(self):
        return self.step_action

    class Meta:
        db_table = 'api_case_step'


class ApiTestBatch(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    tester = models.ForeignKey(User, null=True, on_delete=models.DO_NOTHING)
    result = models.CharField(max_length=1, null=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        db_table = 'api_test_batch'


class ApiCaseResult(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    batch = models.ForeignKey(ApiTestBatch, null=False, on_delete=models.CASCADE)
    case = models.ForeignKey(ApiCase, null=False, on_delete=models.CASCADE)
    result = models.CharField(max_length=1, null=True)
    info = models.CharField(max_length=512, null=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        db_table = 'api_case_result'


class ApiStepResult(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    batch = models.ForeignKey(ApiTestBatch, null=False, on_delete=models.CASCADE)
    case = models.ForeignKey(ApiCaseResult, null=False, on_delete=models.CASCADE)
    step = models.ForeignKey(ApiCaseStep, null=False, on_delete=models.CASCADE)
    result = models.CharField(max_length=1)
    info = models.CharField(max_length=2048, null=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        db_table = 'api_step_result'


class Keyword(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    keyword = models.CharField(max_length=128, null=False)
    description = models.CharField(max_length=256, null=True)
    is_active = models.CharField(max_length=1, null=False, default='1')

    class Meta:
        db_table = 'api_keyword'




