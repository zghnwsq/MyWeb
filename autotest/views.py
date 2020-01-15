from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import generic
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import Group, User
# Create your views here.
from Utils.Personal import get_personal, get_menu
from login.models import UserMenu, Menu


class IndexV(LoginRequiredMixin, generic.ListView):
    template_name = 'autotest/run_his.html'
    context_object_name = 'run_his'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        return context

    def get_queryset(self, **kwargs):
        # todo run history page
        pass
