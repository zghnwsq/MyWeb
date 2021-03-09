import datetime
from django.utils.timezone import *
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import generic
from django.db.models import Q
# from MyWeb import settings
from Utils.Personal import get_personal, get_menu
from Utils.Paginator import *
from Utils.hightchart import chart_series
from .models import *
from django.http import JsonResponse, HttpResponseRedirect
# from django.template.context_processors import csrf
from .exec_test import *
from Utils.MyMixin import URIPermissionMixin
from Utils.decorators import auth_check
# import pytz
from .orm import *

PARENT_MENU = '自动化测试'


class RunHisV(LoginRequiredMixin, URIPermissionMixin, generic.ListView):
    template_name = 'autotest/run_his.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['expand'] = PARENT_MENU
        return context

    def get_queryset(self, **kwargs):
        group = RunHis.objects.using('autotest').values('group').distinct()
        suite = RunHis.objects.using('autotest').values('suite').distinct()
        tester = RunHis.objects.using('autotest').values('tester').distinct()
        context = {
            'group': group,
            'suite': suite,
            'tester': tester
        }
        return context


@login_required
@auth_check
def get_run_his(request):
    # default get params: page=1 limit=10
    # {
    #     "code": 0,
    #     "msg": "",
    #     "count": "",
    #     "data": "[]"
    # }
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    expand = request.GET.get('expand', 'none')
    run_his = filter_run_his(
        tester=request.GET.get('tester', None),
        group=request.GET.get('group', None),
        suite=request.GET.get('suite', None),
        testcase=request.GET.get('testcase', None),
        result=request.GET.get('result', None),
        beg=request.GET.get('beg', None),
        end=request.GET.get('end', None)
    ).values(
        'group', 'suite', 'case', 'title', 'tester', 'result', 'report', 'create_time')
    count = len(run_his)
    data_list = paginator(run_his, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


@login_required
@auth_check
def get_report(request):
    file_path = request.GET.get('path', None)
    if file_path:
        # HtmlTestReport
        if '.html' in file_path:
            return render(request, file_path, {})
        # Pytest html report
        else:
            return HttpResponseRedirect('/static/' + file_path.replace('\\', '/') + '/index.html')
    else:
        report = '<h2>Can not get the report.</h2>'
        return render(request, 'autotest/report.html', {'report': report})


class RunCountV(LoginRequiredMixin, URIPermissionMixin, generic.ListView):
    template_name = 'autotest/run_count.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['expand'] = PARENT_MENU
        return context

    def get_queryset(self, **kwargs):
        group = RunHis.objects.using('autotest').values('group').distinct()
        suite = RunHis.objects.using('autotest').values('suite').distinct()
        context = {
            'group': group,
            'suite': suite,
        }
        return context


@login_required
@auth_check
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
    run_his = filter_run_his(
        group=request.GET.get('group', None),
        suite=request.GET.get('suite', None),
        beg=request.GET.get('beg', None),
        end=request.GET.get('end', None)
    ).values(
        'group', 'suite', 'case', 'title', 'tester', 'result', 'report', 'create_time')
    suite_total = get_suite_total(
        group=request.GET.get('group', None),
        suite=request.GET.get('suite', None)
    )
    run_his = run_his.values('group', 'suite', 'case', res=Min('result'))
    suite_list = [line for line in suite_total]
    count = len(suite_list)
    data_table = []
    for line in suite_list:
        run = len(run_his.filter(group=line.group, suite=line.suite).values('case').distinct())
        if line.count != 0:
            executed_ratio = '%.1f%%' % (run / line.count * 100)
            if run > line.count:
                executed_ratio = '100.0%'
        else:
            executed_ratio = 'error'
        pass_count = int(
            run_his.filter(group=line.group, suite=line.suite).filter(res='0').values('case').distinct().count())
        if line.count > 0 and pass_count <= line.count:
            pass_ratio = '%.1f%%' % (pass_count / line.count * 100)
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
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


class RunHisChartV(LoginRequiredMixin, URIPermissionMixin, generic.ListView):
    template_name = 'autotest/run_his_chart.html'
    context_object_name = 'data'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['expand'] = PARENT_MENU
        return context

    def get_queryset(self, **kwargs):
        run_his = count_by_group()
        series = chart_series(run_his)
        group = RunHis.objects.using('autotest').values('group').distinct()
        context = {
            'series': series,
            'group': group
        }
        return context


@login_required
@auth_check
def get_run_his_chart_data(request):
    run_his = count_by_group(
        group=request.GET.get('group', None),
        beg=request.GET.get('beg', None),
        end=request.GET.get('end', None)
    )
    series = chart_series(run_his)
    return JsonResponse({'data': series})


class ExecutionV(LoginRequiredMixin, URIPermissionMixin, generic.ListView):
    template_name = 'autotest/execution.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['expand'] = PARENT_MENU
        return context

    def get_queryset(self, **kwargs):
        nodes = Node.objects.filter(status='on')
        # functions = RegisterFunction.objects.all()
        group = RegisterFunction.objects.values('group').distinct()
        suite = RegisterFunction.objects.values('suite').distinct()
        function = RegisterFunction.objects.values('func').distinct()
        # executions = Execution.objects.all().values('function__group', 'function__suite', 'method', 'ds_range',
        #                                             'function__function', 'comment', 'status')
        # csrf
        # csrf_token = csrf(self.request)
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'nodes': nodes,
            'group': group,
            'suite': suite,
            'function': function,
            'csrf_token': csrf_token,
        }
        return context


@login_required()
@auth_check
def get_jobs(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    expand = request.GET.get('expand', '')
    jobs = filter_jobs(
        group=request.GET.get('group', None),
        suite=request.GET.get('suite', None),
        func=request.GET.get('func', None)
    )
    count = jobs.count()
    if count > 0:
        data_list = paginator(jobs, int(page), int(limit))
    else:
        data_list = {}
    data_list = get_node_options(data_list)
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


@login_required()
@auth_check
def exec_job(request):
    func = request.POST.get('func', '#').strip()
    mthd = request.POST.get('mthd', '#').strip()
    ds_range = request.POST.get('ds_range', '#').strip()
    node = request.POST.get('node', '#').strip()
    comment = request.POST.get('comment', '#').strip()
    tester = request.session['user_name']
    res = execute_job_asyn(func, mthd, ds_range, node, comment, tester)
    return JsonResponse(res)


def execute_job_asyn(func, mthd, ds_range, node, comment, tester):
    """
       异步调用RPC执行测试用例的方法
    :param func: 对应用例组，测试类
    :param mthd: 对应测试方法
    :param ds_range: 参数范围
    :param node: 执行节点
    :param comment: 备注
    :param tester: 测试人
    :return:
    """
    # 校验是否存在
    func_count = len(RegisterFunction.objects.filter(func=func))
    execution = Execution.objects.exclude(status='running').filter(method=mthd, func__func=func)
    execution_count = len(execution)
    get_node = Node.objects.filter(ip_port=node, status='on')
    node_count = len(get_node)
    if func_count > 0 and execution_count > 0 and node_count > 0:
        # 占用节点
        for row in get_node:
            row.status = 'running'
            row.save()
        # 更新任务状态
        for row in execution:
            row.status = 'running'
            row.ds_range = ds_range
            row.comment = comment
            row.save()
        # 多线程异步执行
        status = job_run(func, mthd, ds_range, node, comment, get_node, tester)
        # 线程异常，更新任务状态
        if 'Error' in status:
            for row in execution:
                row.status = status
                row.save()
        return {"msg": "提交成功!"}
    else:
        return {"msg": "ERROR: 节点注册方法或任务不存在，或执行节点不可用!"}


@login_required()
@auth_check
def new_job_html(request):
    """
        新建任务的弹出层html
    """
    func = RegisterFunction.objects.distinct().values('group', 'suite', 'func').order_by('group', 'suite',
                                                                                         'func').distinct()
    # print(func)
    return render(request, 'autotest/new_job.html', {'func': func})


@login_required()
@auth_check
def save_new_job(request):
    """
        保存新建任务
    """
    func = request.POST.get('func', None).strip()
    mthd = request.POST.get('mthd', None).strip()
    ds_range = request.POST.get('ds_range', None).strip()
    comment = request.POST.get('comment', None).strip()
    if not func or not mthd:
        return JsonResponse({"msg": "ERROR: 节点注册方法和测试方法不能为空!"})
    exec_count = len(Execution.objects.filter(func__func=func, method=mthd))
    get_func = RegisterFunction.objects.filter(func=func)
    if len(get_func) >= 1 and exec_count == 0:
        new = Execution(method=mthd, ds_range=ds_range, comment=comment, func=get_func[0])
        new.save()
        return JsonResponse({"msg": "保存成功!"})
    elif len(get_func) < 1:
        return JsonResponse({"msg": "ERROR: 节点注册方法不存在!"})
    elif exec_count > 0:
        return JsonResponse({"msg": "ERROR: 测试任务重复!"})
    else:
        return JsonResponse({"msg": "ERROR: 未知错误!"})


@login_required()
@auth_check
def del_job(request):
    func = request.POST.get('func', '#').strip()
    mthd = request.get('mthd', '#').strip()
    execution = Execution.objects.filter(method=mthd, func__func=func)
    if len(execution) > 0:
        if len(execution.filter(status='running')) > 0:
            return JsonResponse({"msg": "ERROR: 任务执行中,不能删除!"})
        else:
            for job in execution:
                job.delete()
            return JsonResponse({"msg": "删除成功!"})
    else:
        return JsonResponse({"msg": "ERROR: 未知错误!"})
