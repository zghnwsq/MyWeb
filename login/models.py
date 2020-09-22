# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import User


class Menu(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    text = models.CharField(max_length=32)
    url = models.CharField(max_length=64)
    parent = models.IntegerField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'menu'


class UserMenu(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, blank=True, null=True, on_delete=models.CASCADE)  # This field type is a guess.

    class Meta:
        db_table = 'user_menu'


class PermissionDict(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    permi = models.CharField(max_length=64)
    text = models.CharField(max_length=32)

    def __str__(self):
        return self.text

    class Meta:
        db_table = 'permission_dict'


class UserPermission(models.Model):
    id = models.AutoField(unique=True, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permi = models.ForeignKey(PermissionDict, on_delete=models.CASCADE)

    class Meta:
        db_table = 'user_permission'

