from django.db import models

# Create your models here.


class RunHis(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.CharField(max_length=32, null=False)
    suite = models.CharField(max_length=32, null=False)
    case = models.CharField(max_length=32, null=False)
    title = models.CharField(max_length=64)
    desc = models.CharField(max_length=200)
    tester = models.CharField(max_length=32)
    comment = models.CharField(max_length=200)
    report = models.CharField(max_length=100)
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
    desc = models.CharField(max_length=32, null=False)

    def __str__(self):
        return self.desc

    class Meta:
        db_table = 'res_dict'


class SuiteCount(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    group = models.CharField(max_length=32, null=True)
    suite = models.CharField(max_length=32, null=True)
    count = models.IntegerField(null=True)
