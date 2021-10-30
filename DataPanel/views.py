import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min
from django.http import JsonResponse
from ApiTest.models import ApiGroup, ApiCase
from DataPanel.orm import get_suite_total, filter_api_run_his, count_by_group, count_api_by_group, count_by_result, \
    count_api_by_result
from Utils.CustomView import ListViewWithMenu
from Utils.MyMixin import URIPermissionMixin
from Utils.Paginator import paginator
from Utils.decorators import auth_check
from Utils.hightchart import group_count_and_result_series, result_count_series
from autotest.models import RunHis
from autotest.orm import filter_run_his

PARENT_MENU = '数据看板'


class RunCountV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'DataPanel/run_count.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    def get_queryset(self, **kwargs):
        group = RunHis.objects.values('group').distinct()
        api_group = ApiGroup.objects.values('group').distinct()
        suite = RunHis.objects.values('suite').distinct()
        api_suite = ApiCase.objects.values('suite').distinct()
        tester = RunHis.objects.values('tester').distinct()
        context = {
            'group': group.union(api_group, all=True),
            'suite': suite.union(api_suite, all=True),
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
    # 增加API测试用例统计
    api_run_his = filter_api_run_his(group=request.GET.get('group', None),
                                     suite=request.GET.get('suite', None),
                                     tester=request.GET.get('tester', None),
                                     beg=request.GET.get('beg', None) or recent_90_days,
                                     end=request.GET.get('end', None)).values('case__group__group', 'case__suite',
                                                                              'case__title', res=Min('result'))
    # run_his = run_his.union(api_run_his, all=True)
    # suite_list = [line for line in suite_total]
    count = len(suite_total)
    data_table = []
    for line in list(suite_total):
        run = len(run_his.filter(group=line['group'], suite=line['suite']).values('case').distinct())
        # api用例运行次数要算上参数化, case_title包含轮次,case__titile不包含轮次
        run += len(api_run_his.filter(case__group__group=line['group'],
                                      case__suite=line['suite']).values(
            'case_title').distinct())
        if line['count'] != 0:
            executed_ratio = '%.1f%%' % (run / int(line['count']) * 100)
            if run > line['count']:
                executed_ratio = '100.0%'
        else:
            executed_ratio = 'error'
        pass_count = len(
            run_his.filter(group=line['group'], suite=line['suite']).filter(res='0').values('case').distinct())
        pass_count += len(
            api_run_his.filter(case__group__group=line['group'],
                               case__suite=line['suite'], res='0').values(
                'case_title').distinct()
        )
        if line['count'] > 0 and pass_count <= line['count']:
            pass_ratio = '%.1f%%' % (pass_count / line['count'] * 100)
        elif run >= pass_count > line['count']:
            pass_ratio = '100.0%'
        elif pass_count > run:
            pass_ratio = 'error'
        else:
            pass_ratio = '0.0%'
        data_table.append({
            'group': line['group'],
            'suite': line['suite'],
            'total': line['count'],
            'executed': run,
            'executed_ratio': executed_ratio,
            'pass': pass_count,
            'pass_ratio': pass_ratio}
        )
    data_list = paginator(data_table, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


class RunHisChartV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'DataPanel/run_his_chart.html'
    context_object_name = 'data'
    parent_menu = PARENT_MENU

    def get_queryset(self, **kwargs):
        recent_90_days = datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=-90), '%Y-%m-%d')
        run_his = count_by_group(beg=recent_90_days)
        api_run_his = count_api_by_group(beg=recent_90_days)
        series = group_count_and_result_series(run_his)
        api_series = group_count_and_result_series(api_run_his)
        summary = result_count_series(count_by_result(beg=recent_90_days))
        summary += result_count_series(count_api_by_result(beg=recent_90_days))
        group = RunHis.objects.values('group').distinct()
        api_group = ApiGroup.objects.values('group').distinct()
        context = {
            'series': series + api_series,
            'summary': summary,
            'group': group.union(api_group, all=True)
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
    api_run_his = count_api_by_group(
        group=request.GET.get('group', None),
        beg=request.GET.get('beg', None) or recent_90_days,
        end=request.GET.get('end', None)
    )
    series = group_count_and_result_series(run_his)
    api_series = group_count_and_result_series(api_run_his)
    summary = result_count_series(count_by_result(group=request.GET.get('group', None),
                                                  beg=request.GET.get('beg', None) or recent_90_days,
                                                  end=request.GET.get('end', None)))
    summary += result_count_series(count_api_by_result(group=request.GET.get('group', None),
                                                       beg=request.GET.get('beg', None) or recent_90_days,
                                                       end=request.GET.get('end', None)))
    return JsonResponse({'data': series + api_series, 'summary': summary})

