import datetime
import pytz
from django.utils.timezone import *
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min, Count, CharField
from django.db.models.functions import Trunc, TruncDate, Cast
from django.shortcuts import render
from django.views import generic
from MyWeb import settings
from Utils.Personal import get_personal, get_menu
from Utils.Paginator import *
from .models import *
from django.http import JsonResponse
import pytz


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
    # data_list = [data for data in run_his]
    # # 利用django分页划分数据
    # paginator = Paginator(data_list, int(limit))
    # try:
    #     pg = paginator.page(int(page))
    # except PageNotAnInteger:
    #     pg = paginator.page(1)
    # except EmptyPage:
    #     pg = paginator.page(paginator.num_pages)
    # # Page obj转回list
    # data_list = [data for data in pg]
    data_list = paginator(run_his, int(page), int(limit))
    # data_list = paginator(data_list, int(page), int(limit))
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
    run_his = RunHis.objects.using('autotest').all()
    suite_total = SuiteCount.objects.all().order_by('group', 'suite')
    if request.GET['group']:
        group = request.GET['group'].strip()
        run_his = run_his.filter(group=group)
        suite_total = suite_total.filter(group=group)
    if request.GET['suite']:
        suite = request.GET['suite'].strip()
        run_his = run_his.filter(suite=suite)
        suite_total = suite_total.filter(suite=suite)
    if request.GET['beg']:
        beg = request.GET['beg'].strip().split('-')
        run_his = run_his.filter(create_time__gte=datetime.datetime(int(beg[0]), int(beg[1]), int(beg[2]), 0, 0, 0, tzinfo=utc))
    if request.GET['end']:
        end = request.GET['end'].strip().split('-')
        run_his = run_his.filter(create_time__lte=datetime.datetime(int(end[0]), int(end[1]), int(end[2]), 23, 59, 59, tzinfo=utc))  # pytz.timezone(settings.TIME_ZONE)
    run_his = run_his.values('group', 'suite', 'case', res=Min('result'))
    suite_list = [line for line in suite_total]
    count = len(suite_list)
    data_table = []
    for line in suite_list:
        run = len(run_his.filter(group=line.group, suite=line.suite).values('case').distinct())
        executed_ratio = '%.1f%%' % (run/line.count*100)
        pass_count = int(run_his.filter(group=line.group, suite=line.suite).filter(res='0').values('case').distinct().count())
        if run > 0 and pass_count <= run:
            pass_ratio = '%.1f%%' % (pass_count/run*100)
        elif pass_count > run:
            pass_ratio = 'error'
        else:
            pass_ratio = '0.0%'
        data_table.append({
            'group': line.group,
            'suite': line.suite,
            'total': line.count,
            'executed': run,
            'executed_ratio': executed_ratio,
            'pass': pass_count,
            'pass_ratio': pass_ratio}
        )
    data_list = paginator(data_table, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list, "expand": expand})


class RunHisChartV(LoginRequiredMixin, generic.ListView):
    template_name = 'autotest/run_his_chart.html'
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        return context

    def get_queryset(self, **kwargs):
        # todo run his chart page
        run_his = RunHis.objects.using('autotest').values('group').annotate(
            time=Cast(TruncDate('create_time'), output_field=CharField()), count=Count(1))  # tzinfo=pytz.timezone('US/Pacific')
        # print(run_his)
        names = run_his.values('group').distinct()
        # print(names)
        series = []
        for name in names:
            list_of_group = run_his.filter(group=name['group'])
            # print(list_of_group)
            datas = []
            for data_of_group in list_of_group:
                datas.append([data_of_group['time'], data_of_group['count']])
            series.append({'name': name['group'], 'data': datas})
        # print(series)
        context = {
            'series': series
        }
        return context


