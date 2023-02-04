import datetime
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import LoginView
from django.views import generic
from DataPanel.orm import count_by_group, result_count, count_api_by_group, get_group_total, get_test_total, \
    get_report_total
from MyWeb import settings
from Utils.CustomView import ListViewWithMenu
from Utils.MyMixin import URIPermissionMixin
from Utils.hightchart import group_count_series
from .form import LoginForm, PersonalInfoForm, ChangePasswordFrom
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import HttpResponseRedirect
from django.urls import reverse
from Utils.Personal import get_menu, get_personal
import logging
import requests
from .models import Weather
from SysAdmin.models import Sys_Config


# Create your views here.


class LoginV(LoginView):
    redirect_field_name = 'next'
    template_name = 'login/login.html'
    logger = logging.getLogger('django')
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['next'] = self.request.GET.get('next', '')
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
                # clear_logged_session(user)
                # 清过期session
                request.session.clear_expired()
                if user.is_active:
                    login(request, user)
                    user_name = user.username
                    try:
                        user_group = Group.objects.get(user__username=user_name).name
                    except ObjectDoesNotExist:
                        user_group = ''
                    request.session['user_name'] = user_name
                    request.session['user_group'] = user_group
                    self.logger.info(f'{self.__class__} {user_name} login')
                    request.session['menus'] = get_menu({'user_name': user_name})
                    if redirect:
                        return HttpResponseRedirect(redirect)
                    else:
                        return HttpResponseRedirect(reverse('login:index'))
            else:
                return render(request, 'login/login.html', context={'err': 'Permission Denied!'})
        else:
            return render(request, 'login/login.html', context={'err': 'Invalid Form!'})


def get_weather():
    weather = {}
    result = Weather.objects.get(status='ok')
    if result:
        weather['temperature'] = result.temperature
        weather['humidity'] = result.humidity
        weather['pm25'] = result.pm25
        weather['comfort'] = result.comfort
        weather['skycon'] = settings.skycon_dict[
            result.skycon] if result.skycon in settings.skycon_dict.keys() else result.skycon
        weather['skycon_icon'] = settings.skycon_icon_dict[
            result.skycon] if result.skycon in settings.skycon_icon_dict.keys() else ''
        weather['aqi'] = result.aqi
        weather['air_desc'] = result.air_desc
    return weather


class IndexV(LoginRequiredMixin, generic.ListView):
    template_name = 'login/index.html'
    context_object_name = 'index'  # 要改名

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context['menus'] = get_menu(context)
        self.request.session['menus'] = context['menus']
        context['time'] = datetime.datetime.now().strftime('%Y-%m-%d')
        context['weather'] = get_weather()
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        seven_day = (datetime.datetime.now()+datetime.timedelta(days=-6)).strftime('%Y-%m-%d')
        run_his = count_by_group(beg=seven_day, end=today)
        api_run_his = count_api_by_group(beg=seven_day, end=today).values('group', 'time', 'count')
        series = group_count_series(run_his)
        api_series = group_count_series(api_run_his)
        res_count = result_count(beg=seven_day, end=today)
        group_total = get_group_total()
        test_total = get_test_total()
        report_total = get_report_total()
        context['data'] = {'series': series + api_series, 'result': res_count, 'group_total': group_total,
                           'test_total': test_total, 'report_total': report_total}
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
    context['menus'] = request.session.get('menus', [])
    context['time'] = datetime.datetime.now().strftime('%Y-%m-%d %A')
    context['message'] = 'Permission Denied!'
    return render(request, 'login/index.html', context=context)


class PersonalInfoV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'login/personal.html'
    logger = logging.getLogger('django')
    context_object_name = 'info'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context = get_personal(self.request, context)
    #     context['menus'] = self.request.session.get('menus', [])
    #     return context

    def get_queryset(self, **kwargs):
        username = self.request.session['user_name']
        info = User.objects.get(username=username)
        context = {'personal': info}
        return context

    def post(self, request, *args, **kwargs):
        info = PersonalInfoForm(request.POST)
        passwd = ChangePasswordFrom(request.POST)
        msg = '没有改变.'
        username = request.session['user_name']
        if info.is_valid():
            email = request.POST.get('email', '')
            csrf = request.POST.get('csrfmiddlewaretoken', '')
            cs = request.session.get('email_csrf', '')
            old_email = User.objects.get(username=username).email
            if cs and csrf == cs:
                msg = '请勿重复提交!'
            elif email == old_email:
                pass
            else:
                request.session['email_csrf'] = csrf
                self.logger.info(f'Email: {email}')
                if email:
                    User.objects.filter(username=username).update(email=email)
                    msg = '修改成功.'
                else:
                    msg = '邮箱不能为空!'
        if passwd.is_valid():
            old_pwd = request.POST.get('old_pwd', '')
            new_pwd = request.POST.get('new_pwd', '')
            repeat_pwd = request.POST.get('repeat_pwd', '')
            self.logger.info(f'Old: {old_pwd}, new: {new_pwd}, repeat: {repeat_pwd}')
            csrf = request.POST.get('csrfmiddlewaretoken', '')
            cs = request.session.get('pwd_csrf', '')
            if cs and csrf == cs:
                msg = '请勿重复提交!'
            elif new_pwd != repeat_pwd:
                msg = '两次输入密码不一致!'
            else:
                request.session['pwd_csrf'] = csrf
                if old_pwd and new_pwd and repeat_pwd:
                    user = authenticate(request, username=username, password=old_pwd)
                    if user is not None:
                        encode_pwd = make_password(new_pwd)
                        User.objects.filter(username=username).update(password=encode_pwd)
                        msg = '修改成功.'
                    else:
                        msg = '原密码错误!'
                else:
                    msg = '密码不能为空!'
        context = {'menus': self.request.session.get('menus', []), 'message': msg}
        context = get_personal(self.request, context)
        info = User.objects.get(username=username)
        context['info'] = {'personal': info}
        return render(request, 'login/personal.html', context=context)


