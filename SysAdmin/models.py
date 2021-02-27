from django.db import models

# Create your models here.


class Sys_Config(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    dict_key = models.CharField(max_length=32)
    dict_value = models.CharField(max_length=64)
    description = models.CharField(max_length=64)

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'sys_config'







