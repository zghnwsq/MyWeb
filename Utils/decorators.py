# coding:utf-8
from functools import wraps
from django.http import JsonResponse
# from django.shortcuts import render
# from django.urls import reverse
from MyWeb import settings
from login.models import *


def auth_check(func):
    """
    鉴权修饰器
    @wraps(view_func)的作用: 不改变使用装饰器的原有函数的结构(如__name__, __doc__)
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
        # 刷新session过期时间
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        return func(request, *args, **kwargs)
    return check





