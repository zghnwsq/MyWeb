from django.db import models

# Create your models here.


class Sys_Config(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    key = models.CharField(max_length=32)
    value = models.CharField(max_length=64)
    desc = models.CharField(max_length=64)

    def __str__(self):
        return self.desc

    class Meta:
        db_table = 'sys_config'







