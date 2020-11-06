# coding:utf-8
from functools import wraps
from django.http import JsonResponse
# from django.shortcuts import render
# from django.urls import reverse
from login.models import *


def auth_check(func):
    """
    鉴权修饰器
    :param func: method view function
    :return: 鉴权通过，执行原视图方法；鉴权不通过，则返回报错json
    """
    @wraps(func)
    def check(request, *args, **kwargs):
        # print(request.user)
        path_info = request.path_info.strip('/')
        # print(path_info)
        has_permi = UserPermission.objects.filter(user=request.user).filter(permi__permi=path_info)
        if not has_permi:
            # raise PermissionDenied('Permission Denied!')
            if request.user.is_authenticated:
                return JsonResponse({"code": 403, "msg": "Permission Denied!"})
            else:
                return JsonResponse({"code": 403, "msg": "Login Required! Permission Denied!"})
        return func(request, *args, **kwargs)
    return check





