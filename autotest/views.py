from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic
from Utils.Personal import get_personal, get_menu
from .models import *
from django.http import JsonResponse


class RunHisV(LoginRequiredMixin, generic.ListView):
    template_name = 'autotest/run_his.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        return context

    def get_queryset(self, **kwargs):
        # todo run history page
        group = RunHis.objects.using('autotest').values('group').distinct()
        suite = RunHis.objects.using('autotest').values('suite').distinct()
        tester = RunHis.objects.using('autotest').values('tester').distinct()
        context = {
            'group': group,
            'suite': suite,
            'tester': tester,
        }
        return context


@login_required
def get_run_his(request):
    # default get params: page=1 limit=10
    # {
    #     "code": 0,
    #     "msg": "",
    #     "count": "",
    #     "data": "[]"
    # }
    page = request.GET['page'] or '0'
    limit = request.GET['limit'] or '30'
    expand = ''
    if 'expand' in request.GET:
        expand = request.GET['expand']
    run_his = RunHis.objects.using('autotest').all().order_by('-create_time').values('group', 'suite', 'case', 'title', 'tester', 'result', 'report', 'create_time')
    if 'tester' in request.GET and request.GET['tester']:
        tester = str(request.GET['tester']).strip()
        run_his = run_his.filter(tester=tester)
    if 'group' in request.GET and request.GET['group']:
        group = str(request.GET['group']).strip()
        run_his = run_his.filter(group=group)
    if 'suite' in request.GET and request.GET['suite']:
        suite = str(request.GET['suite']).strip()
        run_his = run_his.filter(suite=suite)
    if 'testcase' in request.GET and request.GET['testcase']:
        testcase = str(request.GET['testcase']).strip()
        run_his = run_his.filter(case=testcase)
    if 'result' in request.GET and request.GET['result']:
        result = str(request.GET['result']).strip()
        run_his = run_his.filter(result=result)
    count = run_his.count()
    for line in run_his:
        result = ResDict.objects.using('autotest').filter(result=line['result'])[0] or 'null'
        line['result'] = result.desc
        line['create_time'] = line['create_time'].strftime("%Y-%m-%d %H:%M:%S")
    data_list = [data for data in run_his]
    # 利用django分页划分数据
    paginator = Paginator(data_list, int(limit))
    try:
        pg = paginator.page(int(page))
    except PageNotAnInteger:
        pg = paginator.page(1)
    except EmptyPage:
        pg = paginator.page(paginator.num_pages)
    # Page obj转回list
    data_list = [data for data in pg]
    # return json
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list, "expand": expand})


@login_required
def get_report(request):
    file_path = request.GET['path']
    if file_path:
        return render(request, file_path, {})
    else:
        report = '<h2>Can not get the report.</h2>'
        return render(request, 'autotest/report.html', {'report': report})


class RunCountV(LoginRequiredMixin, generic.ListView):
    template_name = 'autotest/run_count.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        return context

    def get_queryset(self, **kwargs):
        # todo run count page
        group = RunHis.objects.using('autotest').values('group').distinct()
        suite = RunHis.objects.using('autotest').values('suite').distinct()
        context = {
            'group': group,
            'suite': suite,
        }
        return context


@login_required
def get_run_count(request):
    # default get params: page=1 limit=10
    # {
    #     "code": 0,
    #     "msg": "",
    #     "count": "",
    #     "data": "[]"
    # }
    page = request.GET['page'] or '0'
    limit = request.GET['limit'] or '30'
    expand = ''
    if 'expand' in request.GET:
        expand = request.GET['expand']
    # todo return data
    run_his = RunHis.objects.using('autotest').all().values('group', 'suite', 'result')
    if request.GET['group']:
        gruop = request.GET['group'].strip()
        run_his = run_his.filter(gruop=gruop)
    elif request.GET['suite']:
        suite = request.GET['suite'].strip()
        run_his = run_his.filter(suite=suite)
    elif request.GET['beg']:
        beg = request.GET['beg'].strip()





