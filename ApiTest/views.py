import datetime
import json
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods
from MyWeb import settings
from Utils.CustomView import ListViewWithMenu
from Utils.MyMixin import URIPermissionMixin
from Utils.Paginator import paginator
from Utils.decorators import auth_check
from .JobRunner import api_job_run
from .form import *
from .models import *
from Utils.JsonEncoder import DateEncoder
from django.db import transaction

PARENT_MENU = r'接口自动化\\(Codeless\\)'


class ApiGroupV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'ApiTest/api_group.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    def get_queryset(self, **kwargs):
        group = ApiGroup.objects.values('group').distinct()
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'group': group,
            'csrf_token': csrf_token,
        }
        return context


@auth_check
@login_required
def get_groups(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    groups = ApiGroup.objects.filter(status='1').values('id', 'group', 'author__username').order_by('id')
    if len(groups) > 0:
        data_list = paginator(groups, int(page), int(limit))
    else:
        data_list = {}
    return JsonResponse({"code": 0, "msg": "", "count": len(groups), "data": data_list})


@auth_check
@login_required
@require_http_methods(['POST'])
def update_group(request):
    req_json = json.loads(request.body)
    group_id = req_json.get('group_id', None)
    group = req_json.get('group', '')
    if isinstance(group_id, int) and group:
        if ApiGroup.objects.get(id=group_id).author == request.user.id or request.session['user_group'] in settings.MNAGER_GROUPS:
            res = ApiGroup.objects.filter(id=group_id).update(group=group)
            msg = f'成功更新{res}条记录.'
        else:
            msg = 'ERROR: 当前用户没有更新此用例组权限.'
    else:
        msg = 'ERROR: 请求内容有误'
    return JsonResponse({'msg': msg})


@auth_check
@login_required
@require_http_methods(['POST'])
def del_group(request):
    req_json = json.loads(request.body)
    group_id = req_json.get('group_id', None)
    if isinstance(group_id, int):
        has_case = ApiCase.objects.filter(group__id=group_id)
        if len(has_case) > 1:
            msg = f'用例组下存在{len(has_case)}条用例,请删除后重试.'
        else:
            if ApiGroup.objects.get(id=group_id).author == request.user.id or request.session['user_group'] in settings.MNAGER_GROUPS:
                res = ApiGroup.objects.filter(id=group_id).update(status='0')
                msg = f'成功删除{res[0]}条记录.'
            else:
                msg = 'ERROR: 当前用户没有删除此用例组权限.'
    else:
        msg = 'ERROR: 请求内容有误.'
    return JsonResponse({'msg': msg})


@auth_check
@login_required
def new_group(request):
    if request.method == 'GET':
        return render(request, 'ApiTest/new_group.html')
    if request.method == 'POST':
        req_json = json.loads(request.body)
        group = req_json.get('group', None)
        if group:
            ApiGroup(group=group, author=request.user, status='1').save()
            msg = '创建成功'
        else:
            msg = 'ERROR: 请求内容有误.'
        return JsonResponse({'msg': msg})


@auth_check
@login_required
@require_http_methods(['GET'])
def get_group_env(request):
    group_id = request.GET.get('group_id', None)
    if group_id:
        group = ApiGroup.objects.filter(id=group_id)
        if group:
            envs = ApiGroupEnv.objects.filter(group=group_id).values('id', 'group_id', 'env_key', 'env_value')
            return render(request, 'ApiTest/api_group_env.html',
                          {'group_id': group_id, 'data': json.dumps(list(envs))})
        else:
            msg = 'ERROR: 用例不存在.'
    else:
        msg = 'ERROR: 请求内容有误.'
    return JsonResponse({'msg': msg})


@auth_check
@login_required
def edit_group_env(request):
    if request.method == 'GET':
        group_id = request.GET.get('group_id', None)
        if group_id:
            group = ApiGroup.objects.filter(id=group_id)
            if group:
                envs = ApiGroupEnv.objects.filter(group=group_id).values('id', 'group_id', 'env_key', 'env_value')
                return JsonResponse({"code": 0, "msg": "", "count": len(envs), "data": list(envs)})
            else:
                msg = 'ERROR: 用例不存在.'
        else:
            msg = 'ERROR: 请求内容有误.'
        return JsonResponse({'msg': msg})
    if request.method == 'POST':
        req_json = json.loads(request.body)
        group_id = req_json.get('group_id', None)
        data = req_json.get('data', None)
        if group_id and data:
            update, new, error = 0, 0, 0
            group = ApiGroup.objects.filter(id=group_id)
            if group:
                for row in data:
                    # 空值跳过
                    if not row['env_key'] or not row['env_value']:
                        error += 1
                        continue
                    # id存在更新
                    if 'id' in row.keys() and row['id']:
                        is_key_exist = ApiGroupEnv.objects.filter(group=group_id, env_key=row['env_key']).exclude(id=row['id'])
                        # 重复key校验
                        if is_key_exist:
                            error += 1
                            continue
                        update += ApiGroupEnv.objects.filter(id=row['id'], group=group_id).update(env_key=row['env_key'], env_value=row['env_value'])
                    # id不存在新增
                    else:
                        is_key_exist = ApiGroupEnv.objects.filter(group=group_id, env_key=row['env_key'])
                        # 重复key校验
                        if is_key_exist:
                            error += 1
                            continue
                        ApiGroupEnv(group=group[0], env_key=row['env_key'], env_value=row['env_value']).save()
                        new += 1
                msg = f'保存成功,更新{update}条, 新增{new}条; 跳过错误数据{error}条.'
            else:
                msg = 'ERROR: 用例组不存在.'
        else:
            msg = 'ERROR: 请求内容有误.'
        return JsonResponse({'msg': msg})


@auth_check
@login_required
@require_http_methods(['POST'])
def del_group_env(request):
    req_json = json.loads(request.body)
    env_id = req_json.get('env_id', None)
    if env_id:
        is_exist = ApiGroupEnv.objects.filter(id=env_id)
        if is_exist:
            is_exist.delete()
            msg = '删除成功.'
        else:
            msg = 'ERROR: 该变量不存在.'
    else:
        msg = 'ERROR: 请求内容有误.'
    return JsonResponse({'msg': msg})


class ApiCaseV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'ApiTest/api_case.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    def get_queryset(self, **kwargs):
        group = ApiGroup.objects.values('group').distinct()
        suite = ApiCase.objects.values('suite').distinct()
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'group': group,
            'suite': suite,
            'csrf_token': csrf_token,
        }
        return context


@auth_check
@login_required
def get_cases(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    group = request.GET.get('group', None)
    suite = request.GET.get('suite', None)
    cases = ApiCase.objects.all()
    if group:
        cases = cases.filter(group__group=group)
    if suite:
        cases = cases.filter(suite=suite)
    cases = cases.values('id', 'group__group', 'suite', 'title', 'author__username').order_by('group__group', 'suite')
    if len(cases) > 0:
        data_list = paginator(cases, int(page), int(limit))
    else:
        data_list = {}
    return JsonResponse({"code": 0, "msg": "", "count": len(cases), "data": data_list})


@auth_check
@login_required
@require_http_methods(['POST'])
def update_case(request):
    req_json = json.loads(request.body)
    form = CaseForm(req_json)
    if form.is_valid():
        case_id = form.cleaned_data.get('id')
        suite = form.cleaned_data.get('suite')
        title = form.cleaned_data.get('title')
        if not suite or not title:
            msg = 'ERROR: suite或title不能为空.'
        else:
            if ApiCase.objects.get(id=case_id).author == request.user.id or request.session['user_group'] in settings.MNAGER_GROUPS:
                ApiCase.objects.filter(id=case_id).update(suite=suite, title=title)
                msg = '更新成功.'
            else:
                msg = 'ERROR: 当前用户没有更新此用例权限.'
    else:
        msg = 'ERROR: 请求数据有误.'
    return JsonResponse({'msg': msg})


@auth_check
@login_required
def del_case(request):
    req_json = json.loads(request.body)
    msg = ''
    print(req_json)
    beg = time.time()
    if 'cases' in req_json.keys():
        succ = []
        not_exists = []
        no_right = []
        for case in req_json['cases']:
            form = CaseForm(case)
            if form.is_valid():
                case_id = form.cleaned_data.get('id')
                if ApiCase.objects.get(id=case_id).author == request.user.id or request.session['user_group'] in settings.MNAGER_GROUPS:
                    case = ApiCase.objects.filter(id=case_id)
                    if case:
                        # on_delete=models.CASCADE 自动删除关联记录
                        # case_steps = ApiCaseStep.objects.filter(case=case[0])
                        # if case_steps:
                        #     case_steps.delete()
                        case.delete()
                        succ.append(case_id)
                    else:
                        not_exists.append(case_id)
                else:
                    no_right.append(case_id)
        if succ:
            msg += f'Case_id: {succ}  删除成功. '
        if not_exists:
            msg += f'Case_id: {not_exists}  用例不存在. '
        if no_right:
            msg += f'ERROR: 当前用户没有删除此用例权限, case_id: {no_right}. '
    else:
        msg = 'ERROR: 请求数据有误.'
    end = time.time()
    print(f'删除用时: {end - beg} s.')
    return JsonResponse({'msg': msg})


@auth_check
@login_required
def new_case(request):
    if request.method == 'GET':
        group = ApiGroup.objects.filter(status='1')
        return render(request, 'ApiTest/new_case.html', {'group': group})
    if request.method == 'POST':
        req_json = json.loads(request.body)
        group = req_json.get('group', None)
        suite = req_json.get('suite', None)
        title = req_json.get('title', None)
        has_group = ApiGroup.objects.filter(id=group)
        if suite and title and len(has_group) > 0:
            ApiCase(group=has_group[0], suite=suite, title=title, author=request.user).save()
            msg = '创建成功'
        else:
            msg = 'ERROR: 请求内容有误或不存在该用例组.'
        return JsonResponse({'msg': msg})


@auth_check
@login_required
def edit_case(request):
    # step edit layer
    if request.method == 'GET':
        case_id = request.GET.get('case_id', '')
        if case_id:
            case = ApiCase.objects.filter(id=case_id)
            if len(case) == 1:
                steps = ApiCaseStep.objects.filter(case__id=case_id).order_by('step_order').values('id', 'step_action',
                                                                                                   'step_p1',
                                                                                                   'step_p2', 'step_p3',
                                                                                                   'case', 'title',
                                                                                                   'step_order')
                keywords = Keyword.objects.filter(is_active='1').values('keyword', 'description')
                cases = ApiCase.objects.exclude(id=case_id).order_by('id').values('id', 'title')
                return render(request, 'ApiTest/api_case_steps.html',
                              {'case_id': case_id, 'title': case[0].title, 'data': json.dumps(list(steps)),
                               'keywords': json.dumps(list(keywords)), 'cases': json.dumps(list(cases))})
            else:
                msg = 'ERROR: 没有此用例.'
        else:
            msg = 'ERROR: 请求内容有误.'
        return JsonResponse({'msg': msg})
    # save steps
    if request.method == 'POST':
        req_json = json.loads(request.body)
        case_id = req_json.get('case_id', None)
        data = req_json.get('data', None)
        if case_id and data:
            has_case = ApiCase.objects.filter(id=int(case_id))
            if has_case:
                # 清空
                # ApiCaseStep.objects.filter(case=has_case[0]).delete()
                batch = []
                index = 0
                created, updated, deleted = [], [], []
                with transaction.atomic():
                    # 事务回滚点
                    save_id = transaction.savepoint()
                    for step in data:
                        if step:
                            if 'id' in step.keys():
                                is_exists = ApiCaseStep.objects.filter(id=step['id'])
                                if is_exists:
                                    is_exists.update(step_action=step['step_action'], step_p1=step['step_p1'],
                                                     step_p2=step['step_p2'], step_p3=step['step_p3'], title=step['title'],
                                                     step_order=index)
                                    updated.append(step['id'])
                            else:
                                batch.append(ApiCaseStep(case=has_case[0], step_action=step['step_action'], step_p1=step['step_p1'],
                                                         step_p2=step['step_p2'], step_p3=step['step_p3'], title=step['title'],
                                                         step_order=index))
                            index += 1
                    # 删除新增顺序不能变
                    deleted = ApiCaseStep.objects.filter(case=has_case[0]).exclude(id__in=updated).delete()
                    if index > 0:
                        created = ApiCaseStep.objects.bulk_create(batch)
                    if len(created) + len(updated) != len(data):
                        transaction.savepoint_rollback(save_id)
                        msg = 'ERROR: 数据更新错误.'
                    else:
                        transaction.savepoint_commit(save_id)
                        msg = f'保存成功,新增{len(created)}条, 更新{len(updated)}条, 删除{deleted[0]}条.'
            else:
                msg = 'ERROR: 用例不存在.'
        else:
            msg = 'ERROR: 请求内容有误.'
        return JsonResponse({'msg': msg})


@auth_check
@login_required
@require_http_methods(['POST'])
def duplicate_case(request):
    req_json = json.loads(request.body)
    print(req_json)
    beg = time.time()
    if 'cases' in req_json.keys():
        cases = req_json['cases']
        tester = request.user
        with transaction.atomic():
            # 事务回滚点
            save_id = transaction.savepoint()
            try:
                count = 0
                for case in cases:
                    target_case = ApiCase.objects.filter(id=case['id'])
                    if target_case:
                        copy_case = ApiCase(group=target_case[0].group, suite=target_case[0].suite,
                                            title=target_case[0].title + ' 复写', author=tester)
                        copy_case.save()
                        target_case_step = ApiCaseStep.objects.filter(case=target_case[0]).values('step_action',
                                                                                                  'step_p1', 'step_p2',
                                                                                                  'step_p3',
                                                                                                  'step_order', 'title')
                        if target_case_step:
                            steps = []
                            for step in target_case_step:
                                steps.append(ApiCaseStep(case=copy_case, step_action=step['step_action'], step_p1=step['step_p1'],
                                                         step_p2=step['step_p2'], step_p3=step['step_p3'],
                                                         step_order=step['step_order'],
                                                         title=step['title']))
                            res = ApiCaseStep.objects.bulk_create(steps)
                            count += len(res)
                info = f'共复写{len(cases)}条用例, {count}行测试步骤.'
            except Exception as e:
                transaction.savepoint_rollback(save_id)
                msg = '复写用例失败! ' + e.__str__()
            else:
                # 提交事务
                transaction.savepoint_commit(save_id)
                msg = '复写用例成功!' + info
    else:
        msg = '请求内容不正确!'
    end = time.time()
    print(f'复写用时: {end - beg} s.')
    return JsonResponse({'msg': msg})


@auth_check
@login_required
def get_steps(request):
    case_id = request.GET.get('case_id', '')
    # 前台分页
    # page = request.GET.get('page', '1')
    # limit = request.GET.get('limit', '30')
    steps = ApiCaseStep.objects.filter(case__id=case_id).order_by('step_order').values('id', 'step_action', 'step_p1',
                                                                                       'step_p2', 'step_p3', 'case',
                                                                                       'step_order', 'title')
    keywords = Keyword.objects.filter(is_active='1').values('keyword', 'description')
    # if len(steps) > 0:
    #     data_list = paginator(steps, int(page), int(limit))
    # else:
    #     data_list = []
    return JsonResponse({"code": 0, "msg": "", "count": len(steps), "data": list(steps), "keywords": list(keywords)})


class ApiJobV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'ApiTest/api_job.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    def get_queryset(self, **kwargs):
        group = ApiGroup.objects.values('group').distinct()
        suite = ApiCase.objects.values('suite').distinct()
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'group': group,
            'suite': suite,
            'csrf_token': csrf_token,
        }
        return context


@auth_check
@login_required
@require_http_methods(['POST'])
def exec_job(request):
    req_json = json.loads(request.body)
    print(req_json)
    if 'cases' in req_json.keys():
        cases = req_json['cases']
        tester = request.user.username
        debug = True if req_json.get('debug', 'False') == 'True' else False
        api_job_run(cases, tester, debug)
        msg = '任务提交成功!'
    else:
        msg = '请求内容不正确!'
    return JsonResponse({'msg': msg})


class ApiResultV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'ApiTest/api_result.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    def get_queryset(self, **kwargs):
        group = ApiGroup.objects.values('group').distinct()
        suite = ApiCase.objects.values('suite').distinct()
        context = {
            'group': group,
            'suite': suite,
        }
        return context


@auth_check
@login_required
def get_result(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    group = request.GET.get('group', None)
    suite = request.GET.get('suite', None)
    recent_90_days = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=-90), '%Y-%m-%d')
    beg = request.GET.get('beg', None) or recent_90_days
    end = request.GET.get('end', None)
    batch = ApiTestBatch.objects.all()
    if beg:
        beg = str(beg).strip()
        if ':' in beg:
            edge = datetime.datetime.strptime(beg, '%Y-%m-%d %H:%M:%S')
        else:
            edge = datetime.datetime.strptime(f'{beg} 00:00:00', '%Y-%m-%d %H:%M:%S')
        batch = batch.filter(create_time__gte=edge)
    if end:
        end = str(end).strip()
        if ':' in end:
            edge = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        else:
            edge = datetime.datetime.strptime(f'{end} 23:59:59', '%Y-%m-%d %H:%M:%S')
        batch = batch.filter(create_time__lte=edge)
    if group:
        batch = batch.filter(apicaseresult__case__group=group)
    if suite:
        batch = batch.filter(apicaseresult__case__suite=suite)
    batch = batch.values('id', 'tester', 'result', 'create_time').order_by('-create_time')
    if len(batch) > 0:
        data_list = paginator(batch, int(page), int(limit))
    else:
        data_list = {}
    return JsonResponse({"code": 0, "msg": "", "count": len(batch), "data": data_list})


@auth_check
@login_required
def get_case_result(request):
    batch_id = request.GET.get('batch', None)
    if batch_id:
        case_result = ApiCaseResult.objects.filter(batch=batch_id).values('id', 'batch', 'case_title', 'result', 'info',
                                                                          'create_time').order_by('id')
        return JsonResponse({"code": 0, "msg": "", "count": len(case_result), "data": list(case_result)})
    else:
        return JsonResponse({"code": 0, "msg": "缺少批次号!", "count": 0, "data": []})


@auth_check
@login_required
def get_steps_result(request):
    case_result_id = request.GET.get('case_result_id', None)
    if case_result_id:
        step_result = ApiStepResult.objects.filter(case=case_result_id).values('batch', 'case__case_title',
                                                                               'step_action',
                                                                               # 'step__step_action',
                                                                               'step_title',
                                                                               # 'step__title',
                                                                               'result', 'info',
                                                                               'create_time').order_by('id')
        return render(request, 'ApiTest/api_step_result.html', {'steps': json.dumps(list(step_result), cls=DateEncoder)})
    else:
        return JsonResponse({"code": 0, "msg": "请求参数不正确!", "count": 0, "data": []})
