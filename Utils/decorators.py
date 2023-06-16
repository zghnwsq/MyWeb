# coding:utf-8
import json
from functools import wraps
from django.http import JsonResponse, HttpResponse
# from django.shortcuts import render
# from django.urls import reverse
from MyWeb import settings
from Utils.JsonSerializerForm import InvalidFormException
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


def json_serializer(serializer_form):
    """
    Json请求反序列化,将json对象赋给request.data变量
    :param serializer_form: JsonSerializerForm子类, 合法则返回字典, 非法则返回报错HttpResponse
    :return: Response
    """
    def decorator(func):
        @wraps(func)
        def serializer_request(request, *args, **kwargs):
            if request.method == 'POST':
                try:
                    req_json = json.loads(request.body)
                    req = serializer_form(req_json).get_data()
                except ValueError:
                    return HttpResponse(status=400, content='{"msg": "Bad Request: Json Serialize Error"}',
                                        content_type='application/json')
                except InvalidFormException as e:
                    return HttpResponse(status=400, content=f'{{"msg": "Request Not Valid: {e}"}}',
                                        content_type='application/json')
                request.data = req
            return func(request, *args, **kwargs)
        return serializer_request
    return decorator

