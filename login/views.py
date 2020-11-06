import datetime

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views import generic
from login.models import UserMenu, Menu
from .form import LoginForm
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import Group, User
from Utils.Personal import *
from django.utils import timezone
from django.contrib.sessions.models import Session
import logging


# Create your views here.


class LoginV(LoginView):
    redirect_field_name = 'next'
    template_name = 'login/login.html'
    logger = logging.getLogger('django')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['err'] = ''
        return context

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        redirect = request.POST.get('next', '')
        if form.is_valid():
            uname = request.POST['username']
            upassword = request.POST['password']
            user = authenticate(request, username=uname, password=upassword)
            if user is not None:
                clear_logged_session(user)
                if user.is_active:
                    login(request, user)
                    user_name = user.username
                    try:
                        user_group = Group.objects.get(user__username=user_name).name
                    except ObjectDoesNotExist:
                        user_group = ''
                    request.session['user_name'] = user_name
                    request.session['user_group'] = user_group
                    self.logger.info('%s login' % user_name)
                    if redirect:
                        return HttpResponseRedirect(redirect)
                    else:
                        return HttpResponseRedirect(reverse('login:index'))
            else:
                return render(request, 'login/login.html', context={'err': 'Permission Denied!'})
        else:
            return render(request, 'login/login.html', context={'err': 'Invalid Form!'})


class IndexV(LoginRequiredMixin, generic.ListView):
    template_name = 'login/index.html'
    context_object_name = 'index'  # 要改名

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['time'] = datetime.datetime.now().strftime('%Y-%m-%d %A')
        return context

    def get_queryset(self, **kwargs):
        pass


@login_required
def logout_v(request):
    logout(request)
    return HttpResponseRedirect(reverse('login:login'))


@login_required
def permission_denied(request):
    context = get_personal(request, {})
    context = get_menu(context)
    context['time'] = datetime.datetime.now().strftime('%Y-%m-%d %A')
    context['message'] = 'Permission Denied!'
    return render(request, 'login/index.html', context=context)
