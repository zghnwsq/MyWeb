import datetime
import logging
from ApiTest.models import ApiCase, ApiCaseResult
from autotest.models import SuiteCount
from django.db.models import Count, CharField, F, Q
from django.db.models.functions import TruncDate, Cast
from autotest.orm import filter_run_his

logger = logging.getLogger('django')


def filter_api_run_his(tester=None, group=None, suite=None, testcase=None, result=None, beg=None, end=None):
    # run_his = ApiTestBatch.objects.all()
    run_his = ApiCaseResult.objects.all()
    if tester:
        tester = str(tester).strip()
        run_his = run_his.filter(batch__tester__username=tester)
    if group:
        group = str(group).strip()
        run_his = run_his.filter(case__group__group=group)
    if suite:
        suite = str(suite).strip()
        run_his = run_his.filter(case__suite=suite)
    if testcase:
        testcase = str(testcase).strip()
        run_his = run_his.filter(case__title=testcase)
    if result:
        result = str(result).strip()
        run_his = run_his.filter(status=result)
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
    logger.info(run_his.query)
    return run_his


def get_suite_total(group=None, suite=None):
    suite_total = SuiteCount.objects.all().values('group', 'suite', 'count').order_by('group', 'suite')
    if group:
        suite_total = suite_total.filter(group=group)
    if suite:
        suite_total = suite_total.filter(suite=suite)
    # 增加API测试用例统计
    api_suite_total = ApiCase.objects.all().values('group__group', 'suite').order_by('group', 'suite')
    if group:
        api_suite_total = api_suite_total.filter(group__group=group)
    if suite:
        api_suite_total = api_suite_total.filter(suite=suite)
    api_suite_total = api_suite_total.annotate(count=Count('id'))
    logger.info(api_suite_total.query)
    return suite_total.union(api_suite_total, all=True)
    # return suite_total


def count_api_by_group(group=None, beg=None, end=None):
    run_his = filter_api_run_his(group=group, beg=beg, end=end)
    run_his = run_his.values('case__group__group').annotate(group=F('case__group__group'),
                                                            time=Cast(TruncDate('create_time'),
                                                                      output_field=CharField()), count=Count(1))
    logger.info(run_his.query)
    return run_his


def count_api_by_result(group=None, beg=None, end=None):
    """
        根据查询条件，按执行结果、日期分组统计次数
    :param group:
    :param beg:
    :param end:
    :return:
    """
    run_his = filter_api_run_his(group=group, beg=beg, end=end)
    run_his_extra = run_his.annotate(time=Cast(TruncDate('create_time'), output_field=CharField()))
    run_his = run_his_extra.values('result', 'time').annotate(succ=Count('result', Q(result='0')),
                                                              fail=Count('result', Q(result='1')),
                                                              error=Count('result', ~Q(result='0') & ~Q(result='1')))
    logger.info(run_his.query)
    return run_his


def count_by_group(group=None, beg=None, end=None):
    run_his = filter_run_his(group=group, beg=beg, end=end)
    run_his = run_his.values('group').annotate(
        time=Cast(TruncDate('create_time'), output_field=CharField()), count=Count(1))
    logger.info(run_his.query)
    return run_his


def result_count(group=None, beg=None, end=None):
    run_his = filter_run_his(group=group, beg=beg, end=end)
    api_run_his = filter_api_run_his(group=group, beg=beg, end=end)
    pass_count = len(run_his.filter(result='0')) + len(api_run_his.filter(result='0'))
    fail_count = len(run_his.filter(result='1')) + len(api_run_his.filter(result='1'))
    error_count = len(run_his.filter(result='2')) + len(api_run_his.exclude(result='0').exclude(result='1'))
    total = pass_count + fail_count + error_count
    if total > 0:
        pass_pec = pass_count / total
        fail_pec = fail_count / total
        error_pec = error_count / total
    else:
        pass_pec, fail_pec, error_pec = 0.0, 0.0, 0.0
    return {'pass': pass_count, 'fail': fail_count, 'error': error_count, 'pass_pec': pass_pec, 'fail_pec': fail_pec,
            'error_pec': error_pec}


def count_by_result(group=None, beg=None, end=None):
    """
        根据查询条件，按执行结果、日期分组统计次数
    :param group:
    :param beg:
    :param end:
    :return:
    """
    run_his = filter_run_his(group=group, beg=beg, end=end)
    run_his_extra = run_his.annotate(time=Cast(TruncDate('create_time'), output_field=CharField()))
    # 去掉无用字段
    # .extra(
    # select={'res_text': 'select description from res_dict where res_dict.result=run_his.result'})
    # 确保每个日期都有成功、失败、错误三类,
    # res_text=通过,增加succ数据
    # res_text=失败,增加fail
    # res_text=错误,增加error
    run_his = run_his_extra.values('result', 'time').annotate(succ=Count('result', Q(result='0')),
                                                              fail=Count('result', Q(result='1')),
                                                              error=Count('result', Q(result='2')))
    logger.info(run_his.query)
    return run_his

