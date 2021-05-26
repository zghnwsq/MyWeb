import datetime
from django.db.models import Min, Count, CharField, F
from django.db.models.functions import TruncDate, Cast
# from pytz import utc
from .models import *
import copy


def filter_run_his(tester=None, group=None, suite=None, testcase=None, result=None, beg=None, end=None):
    run_his = RunHis.objects.all().order_by('-create_time')
    if tester:
        tester = str(tester).strip()
        run_his = run_his.filter(tester=tester)
    if group:
        group = str(group).strip()
        run_his = run_his.filter(group=group)
    if suite:
        suite = str(suite).strip()
        run_his = run_his.filter(suite=suite)
    if testcase:
        testcase = str(testcase).strip()
        run_his = run_his.filter(case__contains=testcase)
    if result:
        result = str(result).strip()
        run_his = run_his.filter(result=result)
    if beg:
        beg = str(beg).strip()
        if ':' in beg:
            edge = datetime.datetime.strptime(beg, '%Y-%m-%d %H:%M:%S')
        else:
            edge = datetime.datetime.strptime(f'{beg} 00:00:00', '%Y-%m-%d %H:%M:%S')
        run_his = run_his.filter(create_time__gte=edge)
    if end:
        end = str(end).strip()
        if ':' in end:
            edge = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        else:
            edge = datetime.datetime.strptime(f'{end} 23:59:59', '%Y-%m-%d %H:%M:%S')
        run_his = run_his.filter(create_time__lte=edge)
    # 时间转字符串函数仅支持sqlite3
    run_his = run_his.extra(
        select={'result': 'select description from res_dict where res_dict.result=run_his.result'}).extra(
        select={'create_time': "DATE_FORMAT(create_time, %s)"}, select_params=['%Y-%m-%d %H:%i:%s'])
    return run_his


def get_suite_total(group=None, suite=None):
    suite_total = SuiteCount.objects.all().order_by('group', 'suite')
    if group:
        suite_total = suite_total.filter(group=group)
    if suite:
        suite_total = suite_total.filter(suite=suite)
    return suite_total


def count_by_group(group=None, beg=None, end=None):
    run_his = RunHis.objects.all()
    if group:
        run_his = run_his.filter(group=group)
    if beg:
        edge = datetime.datetime.strptime(f'{beg} 00:00:00', '%Y-%m-%d %H:%M:%S')
        run_his = run_his.filter(create_time__gte=edge)
    if end:
        edge = datetime.datetime.strptime(f'{end} 23:59:59', '%Y-%m-%d %H:%M:%S')
        run_his = run_his.filter(create_time__lte=edge)
    run_his = run_his.values('group').annotate(
        time=Cast(TruncDate('create_time'), output_field=CharField()), count=Count(1))
    return run_his


def result_count(group=None, beg=None, end=None):
    run_his = RunHis.objects.all()
    if group:
        run_his = run_his.filter(group=group)
    if beg:
        edge = datetime.datetime.strptime(f'{beg} 00:00:00', '%Y-%m-%d %H:%M:%S')
        run_his = run_his.filter(create_time__gte=edge)
    if end:
        edge = datetime.datetime.strptime(f'{end} 23:59:59', '%Y-%m-%d %H:%M:%S')
        run_his = run_his.filter(create_time__lte=edge)
    pass_count = len(run_his.filter(result='0'))
    fail_count = len(run_his.filter(result='1'))
    error_count = len(run_his.filter(result='2'))
    total = pass_count + fail_count + error_count
    if total > 0:
        pass_pec = pass_count/total
        fail_pec = fail_count/total
        error_pec = error_count/total
    else:
        pass_pec, fail_pec, error_pec = 0.0, 0.0, 0.0
    return {'pass': pass_count, 'fail': fail_count, 'error': error_count, 'pass_pec': pass_pec, 'fail_pec': fail_pec,
            'error_pec': error_pec}


def filter_jobs(group=None, suite=None, func=None):
    jobs = Execution.objects.all().annotate(group=F('func__group'),
                                            suite=F('func__suite'),
                                            funct=F('func__func'),
                                            mthd=F('method'),
                                            tests=F('func__tests')
                                            ).values('group', 'suite',
                                                     'mthd', 'ds_range',
                                                     'funct', 'comment',
                                                     'status', 'tests')
    if group:
        jobs = jobs.filter(func__group=group)
    if suite:
        jobs = jobs.filter(func__suite=suite)
    if func:
        jobs = jobs.filter(func__func=func)
    jobs = jobs.order_by('group', 'suite')
    return jobs


def get_node_options(data_list):
    tmp_list = copy.deepcopy(data_list)
    for data in tmp_list:
        nodes = list(RegisterFunction.objects.filter(func=data['funct'],
                                                     node__in=Node.objects.filter(status='on').values('ip_port')).extra(
            select={
                'tag': 'select tag from autotest_node where ip_port=autotest_registerfunction.node limit 1'}).values(
            'node', 'tag').distinct())
        data['nodes'] = nodes
    return tmp_list







