from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.views import generic
from login.models import UserMenu, Menu
from .form import LoginForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import Group, User
from Utils.Personal import *

# Create your views here.


class LoginV(LoginView):
    redirect_field_name = 'next'
    template_name = 'login/login.html'

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        redirect = request.POST.get('next', '')
        if form.is_valid():
            uname = request.POST['username']
            upassword = request.POST['password']
            user = authenticate(request, username=uname, password=upassword)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    user_name = user.username
                    try:
                        user_group = Group.objects.get(user__username=user_name).name
                    except ObjectDoesNotExist:
                        user_group = ''
                    request.session['user_name'] = user_name
                    request.session['user_group'] = user_group
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
    context_object_name = 'menu_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        user = User.objects.get(username=context['user_name'])
        all_menu = UserMenu.objects.filter(user=user).values('menu')
        first_level = Menu.objects.filter(id__in=all_menu, parent__isnull=True).order_by('order')
        u_menu = []
        for m1 in first_level:
            menu_items = {'url': m1.url, 'text': m1.text}
            second_level = Menu.objects.filter(id__in=all_menu, parent=m1.id).order_by('order')
            childs = []
            for m2 in second_level:
                childs.append({'url': m2.url, 'text': m2.text})
            menu_items['childs'] = childs
            u_menu.append(menu_items)
        context['menus'] = u_menu
        return context

    def get_queryset(self, **kwargs):
        # todo menu
        pass




