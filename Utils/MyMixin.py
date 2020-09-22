# coding:utf-8
# import logging
from django.contrib.auth.mixins import AccessMixin
# from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from login.models import *


class URIPermissionMixin(AccessMixin):

    def dispatch(self, request, *args, **kwargs):
        path_info = request.path_info.strip('/')
        has_permi = UserPermission.objects.filter(user=request.user).filter(permi__permi=path_info)
        if not has_permi:
            # raise PermissionDenied('Permission Denied!')
            if request.user.is_authenticated:
                return HttpResponseRedirect(reverse('login:permission_denied'))
            else:
                return render(request, 'login/login.html', context={'err': 'Permission Denied!'})
        return super().dispatch(request, *args, **kwargs)









