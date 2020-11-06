# coding:utf-8
# import logging
from django.contrib.auth.mixins import AccessMixin
# from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from login.models import *


class URIPermissionMixin(AccessMixin):
    """
    根据URI判断用户访问权限，自定义class view mixin
    """

    def dispatch(self, request, *args, **kwargs):
        """
        重写dispatch，加入权限校验
        :param request: 请求
        :param args: 请求附带参数
        :param kwargs: 请求附带参数
        :return: 如鉴权不通过，跳转页面；通过，则跳回原视图
        """
        path_info = request.path_info.strip('/')
        has_permi = UserPermission.objects.filter(user=request.user).filter(permi__permi=path_info)
        if not has_permi:
            # raise PermissionDenied('Permission Denied!')
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login:permission_denied'))
            else:
                return render(request, 'login/login.html', context={'err': 'Permission Denied!'})
        return super().dispatch(request, *args, **kwargs)









