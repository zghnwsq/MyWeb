from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class ApiGroup(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.CharField(max_length=64, blank=False)
    author = models.ForeignKey(User, blank=False, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=1)

    def __str__(self):
        return self.group

    class Meta:
        db_table = 'api_group'


class ApiGroupEnv(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.ForeignKey(ApiGroup, blank=False, on_delete=models.CASCADE)
    env_key = models.CharField(max_length=256, null=False, blank=False)
    env_value = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.env_key

    class Meta:
        db_table = 'api_group_env'


class ApiCase(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.ForeignKey(ApiGroup, blank=False, on_delete=models.CASCADE)
    suite = models.CharField(max_length=64, blank=False)
    title = models.CharField(max_length=128, blank=False)
    author = models.ForeignKey(User, null=False, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'api_case'


class ApiCaseStep(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    case = models.ForeignKey(ApiCase, blank=False, on_delete=models.CASCADE)
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
    tester = models.CharField(max_length=150, null=True, blank=True)
    result = models.CharField(max_length=1, null=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        db_table = 'api_test_batch'


class ApiCaseResult(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    batch = models.ForeignKey(ApiTestBatch, blank=False, on_delete=models.CASCADE)
    case = models.ForeignKey(ApiCase, null=True, on_delete=models.SET_NULL)
    case_title = models.CharField(max_length=128, null=False)
    result = models.CharField(max_length=1, null=True)
    info = models.CharField(max_length=512, null=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        db_table = 'api_case_result'


class ApiStepResult(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    batch = models.ForeignKey(ApiTestBatch, blank=False, on_delete=models.CASCADE)
    case = models.ForeignKey(ApiCaseResult, blank=False, on_delete=models.CASCADE)
    step = models.ForeignKey(ApiCaseStep, null=True, on_delete=models.SET_NULL)
    step_title = models.CharField(max_length=128, null=True)
    step_action = models.CharField(max_length=128, null=True)
    result = models.CharField(max_length=1)
    info = models.CharField(max_length=2048, null=True)
    create_time = models.DateTimeField(auto_created=True)

    class Meta:
        db_table = 'api_step_result'


class Keyword(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    keyword = models.CharField(max_length=128, blank=False)
    description = models.CharField(max_length=256, null=True)
    list_order = models.IntegerField(blank=False, default=1)
    is_active = models.CharField(max_length=1, blank=False, default='1')

    class Meta:
        db_table = 'api_keyword'


class ApiCaseParam(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    case = models.ForeignKey(ApiCase, blank=False, on_delete=models.CASCADE)
    p_name = models.CharField(max_length=256, blank=False)

    class Meta:
        db_table = 'api_case_param'


class ApiCaseParamValues(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    param = models.ForeignKey(ApiCaseParam, blank=False, on_delete=models.CASCADE)
    p_value = models.CharField(max_length=512, blank=True)

    class Meta:
        db_table = 'api_case_param_values'



