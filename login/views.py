from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import Group


# Create your views here.


class LoginView(LoginView):
    redirect_field_name = 'next'
    template_name = 'login/login.html'

