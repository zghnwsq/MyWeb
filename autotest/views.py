import base64
import json
from django.contrib.auth.decorators import login_required
# from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.mixins import LoginRequiredMixin
# from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
# from django.views import generic
# from django.db.models import Q
# from MyWeb import settings
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView
from Utils.CustomView import ListViewWithMenu
from Utils.Paginator import *
from Utils.hightchart import group_count_and_result_series, result_count_series
from Utils.ReadExcel import *
# from .models import *
from django.http import JsonResponse, HttpResponseRedirect, FileResponse
# from django.template.context_processors import csrf
from .datasource import update_datasource
from .exec_test import *
from Utils.MyMixin import URIPermissionMixin
from Utils.decorators import auth_check
# import pytz
from .form import DataSourceForm, ExecutionForm
from .orm import *
from django.views.decorators.csrf import csrf_exempt
from SysAdmin.models import Sys_Config

PARENT_MENU = '自动化测试'


class RunHisV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'autotest/run_his.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context = get_personal(self.request, context)
    #     context['menus'] = self.request.session.get('menus', [])
    #     context['expand'] = PARENT_MENU
    #     return context

    def get_queryset(self, **kwargs):
        group = RunHis.objects.values('group').distinct()
        suite = RunHis.objects.values('suite').distinct()
        tester = RunHis.objects.values('tester').distinct()
        context = {
            'group': group,
            'suite': suite,
            'tester': tester
        }
        return context


@auth_check
@login_required
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
    # expand = request.GET.get('expand', 'none')
    recent_90_days = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=-90), '%Y-%m-%d')
    run_his = filter_run_his(
        tester=request.GET.get('tester', None),
        group=request.GET.get('group', None),
        suite=request.GET.get('suite', None),
        testcase=request.GET.get('testcase', None),
        result=request.GET.get('result', None),
        beg=request.GET.get('beg', None) or recent_90_days,
        end=request.GET.get('end', None)
    ).values(
        'id', 'group', 'suite', 'case', 'title', 'tester', 'result', 'report', 'comment', 'create_time')
    count = len(run_his)
    data_list = paginator(run_his, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


@auth_check
@login_required
def get_report(request):
    runhis_id = request.GET.get('id', None)
    f_path = RunHis.objects.filter(id=runhis_id)
    if f_path:
        # HtmlTestReport
        if '.html' in f_path[0].report:
            return render(request, f_path[0].report, {})
        # Pytest html report
        else:
            return HttpResponseRedirect('/static/' + f_path.replace('\\', '/') + '/index.html')
    else:
        report = '<h2>Can not get the report.</h2>'
        return render(request, 'autotest/report.html', {'report': report})


@auth_check
@login_required
def update_runhis_comment(request):
    print(request.body)
    req = json.loads(request.body)
    run_his = RunHis.objects.filter(group=req.get('group', ''), suite=req.get('suite', ''), case=req.get('case', ''),
                                    title=req.get('title', ''), report=req.get('report', ''),
                                    create_time=req.get('create_time', '').replace('T', ' '))
    if run_his:
        run_his.update(comment=req.get('comment', ''))
        return JsonResponse({'msg': '备注更新成功!'}, json_dumps_params={'ensure_ascii': False})
    else:
        return JsonResponse({'msg': '测试历史记录不存在!'}, json_dumps_params={'ensure_ascii': False})


class RunCountV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'autotest/run_count.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context = get_personal(self.request, context)
    #     context['menus'] = self.request.session.get('menus', [])
    #     context['expand'] = PARENT_MENU
    #     return context

    def get_queryset(self, **kwargs):
        group = RunHis.objects.values('group').distinct()
        suite = RunHis.objects.values('suite').distinct()
        tester = RunHis.objects.values('tester').distinct()
        context = {
            'group': group,
            'suite': suite,
            'tester': tester
        }
        return context


@auth_check
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
    # expand = ''
    # if 'expand' in request.GET:
    #     expand = request.GET['expand']
    recent_90_days = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=-90), '%Y-%m-%d')
    run_his = filter_run_his(
        group=request.GET.get('group', None),
        suite=request.GET.get('suite', None),
        tester=request.GET.get('tester', None),
        beg=request.GET.get('beg', None) or recent_90_days,
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
        elif run >= pass_count > line.count:
            pass_ratio = '100.0%'
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


class RunHisChartV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'autotest/run_his_chart.html'
    context_object_name = 'data'
    parent_menu = PARENT_MENU

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context = get_personal(self.request, context)
    #     context['menus'] = self.request.session.get('menus', [])
    #     context['expand'] = PARENT_MENU
    #     return context

    def get_queryset(self, **kwargs):
        recent_90_days = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=-90), '%Y-%m-%d')
        run_his = count_by_group(beg=recent_90_days)
        series = group_count_and_result_series(run_his)
        summary = result_count_series(count_by_result(beg=recent_90_days))
        group = RunHis.objects.values('group').distinct()
        context = {
            'series': series,
            'summary': summary,
            'group': group
        }
        return context


@auth_check
@login_required
def get_run_his_chart_data(request):
    # 不带任何条件也默认最近90天
    recent_90_days = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=-90), '%Y-%m-%d')
    run_his = count_by_group(
        group=request.GET.get('group', None),
        beg=request.GET.get('beg', None) or recent_90_days,
        end=request.GET.get('end', None)
    )
    series = group_count_and_result_series(run_his)
    summary = result_count_series(count_by_result(group=request.GET.get('group', None),
                                                  beg=request.GET.get('beg', None) or recent_90_days,
                                                  end=request.GET.get('end', None)))
    return JsonResponse({'data': series, 'summary': summary})


class ExecutionV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'autotest/execution.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context = get_personal(self.request, context)
    #     context['menus'] = self.request.session.get('menus', [])
    #     context['expand'] = PARENT_MENU
    #     return context

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


@auth_check
@login_required()
def get_jobs(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    # expand = request.GET.get('expand', '')
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
@require_http_methods(['POST'])
def exec_job(request):
    req = json.loads(request.body)
    form = ExecutionForm(req)
    if form.is_valid():
        func = form.cleaned_data.get('func', '#').strip()
        mthd = form.cleaned_data.get('mthd', '#').strip()
        ds_range = form.cleaned_data.get('ds_range', '#').strip()
        node = form.cleaned_data.get('node', '#').strip()
        comment = form.cleaned_data.get('comment', '#').strip()
        tester = request.session['user_name']
        res = execute_job_asyn(func, mthd, ds_range, node, comment, tester)
        return JsonResponse(res)
    else:
        return JsonResponse({"msg": "ERROR: 节点注册方法和测试方法不能为空!"})


def execute_job_asyn(func, mthd, ds_range, node, comment, tester):
    """
       异步调用RPC执行测试用例的方法
    :param func: 对应用例组，测试类
    :param mthd: 对应测试方法
    :param ds_range: 参数范围
    :param node: 执行节点 ip:port
    :param comment: 备注
    :param tester: 测试人
    :return: json msg
    """
    # 校验是否存在
    exist_func = RegisterFunction.objects.filter(func=func, node=node)
    execution = Execution.objects.exclude(status='running').filter(method=mthd, func__func=func)
    execution_count = len(execution)
    free_node = Node.objects.filter(ip_port=node, status='on')
    if len(exist_func) > 0 and execution_count == 1 and len(free_node) > 0:
        # 更新关联关系
        execution.update(func=exist_func[0].id)
        # 占用节点
        for row in free_node:
            row.status = 'running'
            row.save()
        # 更新任务状态 任务不允许重复
        execution.update(status='running', ds_range=ds_range, comment=comment)
        # 多线程异步执行
        status = job_run(func, mthd, ds_range, node, comment, get_node, tester)
        # 线程异常，更新任务状态
        if 'Error' in status:
            execution.update(status=status)
        return {"msg": "提交成功!"}
    elif len(exist_func) > 0 and execution_count == 1:
        # 更新关联关系
        execution.update(func=exist_func[0].id)
        # 加入队列
        is_in_queue = len(JobQueue.objects.filter(executioin=execution[0], node=node, status='new'))
        if is_in_queue < 1:
            # 更新信息
            execution.update(status='in job queue', ds_range=ds_range, comment=comment)
            JobQueue(executioin=execution[0], node=node, status='new', tester=tester,
                     create_time=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())).save()
            return {"msg": "提交队列成功!"}
        else:
            return {"msg": "任务已在队列中!"}
    else:
        return {"msg": "ERROR: 节点注册方法或任务不存在，或执行节点不可用!"}


@auth_check
@login_required()
def new_job_html(request):
    """
        新建任务的弹出层html
    """
    func = RegisterFunction.objects.distinct().values('group', 'suite', 'func').order_by('group', 'suite',
                                                                                         'func').distinct()
    # print(func)
    return render(request, 'autotest/new_job.html', {'func': func})


@auth_check
@login_required()
@require_http_methods(['POST'])
def save_new_job(request):
    """
        保存新建任务
    """
    req = json.loads(request.body)
    form = ExecutionForm(req)
    if form.is_valid():
        func = form.cleaned_data.get('func', '#').strip()
        mthd = form.cleaned_data.get('mthd', '#').strip()
        ds_range = form.cleaned_data.get('ds_range', '#').strip()
        comment = form.cleaned_data.get('comment', '#').strip()
    else:
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


@auth_check
@login_required()
@require_http_methods(['POST'])
def del_job(request):
    req = json.loads(request.body)
    form = ExecutionForm(req)
    if form.is_valid():
        func = form.cleaned_data.get('func', '#').strip()
        mthd = form.cleaned_data.get('mthd', '#').strip()
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
    else:
        return JsonResponse({"msg": "ERROR: 节点注册方法和测试方法不能为空!"})


@require_http_methods(['POST'])
@csrf_exempt
def regsiter_node(request):
    msg = ''
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: only support basic authentication for now.
            if auth[0].lower() == "basic":
                auth_token = base64.b64decode(auth[1]).decode()
                db_token = Sys_Config.objects.get(dict_key='Register_Node_Auth').dict_value
                if auth_token != db_token:
                    msg = 'ERROR: token错误!'
                else:
                    req = request.body
                    req_json = json.loads(req)
                    if req_json['type'] == 'update':
                        msg = update_node(req_json)
                    if req_json['type'] == 'node_off':
                        msg = update_node_off(req_json)
        else:
            msg = 'ERROR: HTTP_AUTHORIZATION Invalid'
    else:
        msg = 'ERROR: Required HTTP_AUTHORIZATION'
    return JsonResponse({"msg": msg})


def update_node(req_json):
    if 'host_ip' in req_json.keys() and 'tag' in req_json.keys() and 'func' in req_json.keys():
        host_ip = req_json['host_ip'].strip()
        tag = req_json['host_ip']
        func = req_json['func']
        exist_node = Node.objects.filter(ip_port=host_ip)
        if exist_node:
            exist_node.update(status='on')
        else:
            Node(ip_port=host_ip, tag=tag, status='on').save()
        for mthd_name in func.keys():
            is_exists = RegisterFunction.objects.filter(func=mthd_name, node=host_ip)
            if is_exists:
                is_exists.update(tests=func[mthd_name])
            else:
                split_mthd_name = mthd_name.split('_')
                group = split_mthd_name[0]
                suite_name = split_mthd_name[1]
                RegisterFunction(group=group, suite=suite_name, func=mthd_name, node=host_ip,
                                 tests=func[mthd_name]).save()
        return 'OK'


def update_node_off(req_json):
    host_ip = req_json['host_ip'].strip()
    Node.objects.filter(ip_port=host_ip).update(status='off')
    return 'OK'


@require_http_methods(['POST'])
@csrf_exempt
def update_suite_cases_count(request):
    msg = ''
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2:
            # NOTE: only support basic authentication for now.
            if auth[0].lower() == "basic":
                auth_token = base64.b64decode(auth[1]).decode()
                db_token = Sys_Config.objects.get(dict_key='Register_Node_Auth').dict_value
                if auth_token != db_token:
                    msg = 'ERROR: token错误!'
                else:
                    req = request.body
                    req_json = json.loads(req)
                    test_group = req_json.get('test_group', '')
                    test_suite = req_json.get('test_suite', '')
                    case_count = req_json.get('case_count', '')
                    if not isinstance(case_count, int):
                        msg = 'ERROR: Case_count must be number'
                    else:
                        exist_row = SuiteCount.objects.filter(group=test_group, suite=test_suite)
                        if exist_row:
                            exist_row.update(count=int(case_count))
                        else:
                            SuiteCount(group=test_group, suite=test_suite, count=int(case_count)).save()
                        msg = 'OK'
        else:
            msg = 'ERROR: HTTP_AUTHORIZATION Invalid'
    else:
        msg = 'ERROR: Required HTTP_AUTHORIZATION'
    return JsonResponse({"msg": msg})


@auth_check
@login_required()
@require_http_methods(['POST'])
def update_ds(request):
    form = DataSourceForm(request.POST, request.FILES)
    if form.is_valid():
        ds_name = form.cleaned_data['ds_name']
        file = form.cleaned_data['file']
        msg = update_datasource(ds_name, file)
    else:
        msg = "ERROR: 提交表单错误!"
    return JsonResponse({"msg": msg}, json_dumps_params={'ensure_ascii': False})


class DataSourceV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'autotest/datasource.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    def get_queryset(self, **kwargs):
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'csrf_token': csrf_token,
        }
        return context


@auth_check
@login_required()
def get_ds(request):
    ds_name = request.GET.get('ds_name', '')
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    exist_ds = DataSource.objects.filter(ds_name__contains=ds_name.strip()).values('ds_name', 'update_time').order_by(
        'update_time')
    if len(exist_ds) > 0:
        data_list = paginator(exist_ds, int(page), int(limit))
    else:
        data_list = {}
    return JsonResponse({"code": 0, "msg": "", "count": len(exist_ds), "data": data_list})


@auth_check
@login_required()
@require_http_methods(['POST'])
def download_ds(request):
    ds_name = request.POST.get('ds_name', '')
    exist_ds = DataSource.objects.filter(ds_name=ds_name.strip())
    if exist_ds:
        f_path = os.path.join(settings.DATA_SOURCE_ROOT, exist_ds[0].file_path)
        return FileResponse(open(f_path, 'rb'), as_attachment=True, filename=exist_ds[0].file_name)
    else:
        return JsonResponse({"msg": '数据源不存在!'}, json_dumps_params={'ensure_ascii': False})


class DataSourcePreviewV(LoginRequiredMixin, URIPermissionMixin, ListView):
    template_name = 'autotest/datasource_preview.html'
    context_object_name = 'data'

    def get_queryset(self, **kwargs):
        ds_name = self.request.GET.get('ds_name', '')
        exist_ds = DataSource.objects.filter(ds_name=ds_name.strip())
        context = {}
        if exist_ds:
            f_path = os.path.join(settings.DATA_SOURCE_ROOT, exist_ds[0].file_path)
            if 'xls' in str(f_path.split('.')[-1]):
                sheetnames, excel = read_all_data(f_path)
                context['sheetnames'] = sheetnames
                context['excel'] = excel
            else:
                yaml = ''
                with open(f_path, encoding='utf-8') as file:
                    while True:
                        line = file.readline()
                        if line:
                            yaml += line
                        else:
                            break
                context['yaml'] = yaml
        return context


