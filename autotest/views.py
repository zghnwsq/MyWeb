from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.views import generic
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from Utils.Personal import get_personal, get_menu
from .models import *
from django.core import serializers
import json
from django.http import JsonResponse


class RunHisV(LoginRequiredMixin, generic.ListView):
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


@login_required
def get_run_his(request):
    # default get params: page=1 limit=30
    # {
    #     "count": "",
    #     "data": "[]"
    # }
    page = request.GET['page'] or '0'
    limit = request.GET['limit'] or '30'
    run_his = RunHis.objects.using('autotest').all().order_by('-create_time').values('group', 'suite', 'case', 'title', 'tester', 'result', 'report', 'create_time')
    count = run_his.count()
    for line in run_his:
        result = ResDict.objects.using('autotest').filter(result=line['result'])[0] or 'null'
        line['result'] = result.desc
        line['create_time'] = line['create_time'].strftime("%Y-%m-%d %H:%M:%S")
    data_list = [data for data in run_his]
    print(data_list)
    # paginator = Paginator(run_his, int(limit))
    # try:
    #     pg = paginator.page(int(page))
    # except PageNotAnInteger:
    #     pg = paginator.page(1)
    # except EmptyPage:
    #     pg = paginator.page(paginator.num_pages)
    # format json
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})

