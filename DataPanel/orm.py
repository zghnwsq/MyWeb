import datetime
import logging
from ApiTest.models import ApiCaseResult, ApiGroup
from Utils.Constant import ResultCode
from autotest.models import SuiteCount, RunHis
from django.db.models import Count, CharField, F, Q, Sum
from django.db.models.functions import TruncDate, Cast
from autotest.orm import filter_run_his
from Utils.RawSql import dict_fetch_all, raw_sql_fetch_one

logger = logging.getLogger('django')


def filter_api_run_his(tester=None, group=None, suite=None, testcase=None, result=None, beg=None, end=None):
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
        run_his = run_his.filter(case_title=testcase)
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


def get_suite_total(group='', suite=''):
    suite_total = SuiteCount.objects.all().values('count', 'group', 'suite').order_by('group', 'suite')
    if group:
        suite_total = suite_total.filter(group=group)
    if suite:
        suite_total = suite_total.filter(suite=suite)
    # 增加API测试用例统计
    # 初版##################
    # api_suite_total = ApiCase.objects.all().values('group__group', 'suite').order_by('group', 'suite')
    # if group:
    #     api_suite_total = api_suite_total.filter(group__group=group)
    # if suite:
    #     api_suite_total = api_suite_total.filter(suite=suite)
    # api_suite_total = api_suite_total.annotate(count=Count('id'))
    #######################
    # 第二版################
    # 注意case when在不同数据库区别
    # api_suite_total = ApiCase.objects.all()
    # if group:
    #     api_suite_total = api_suite_total.filter(group__group=group)
    # if suite:
    #     api_suite_total = api_suite_total.filter(suite=suite)
    # api_suite_total = api_suite_total.extra(select={
    #     'count': 'select case when max(a.n) is null then 1 else max(a.n) end max_count from (select count(v.p_value) n from api_case_param p, api_case_param_values v where p.id=v.param_id and p.case_id=api_case.id group by p.p_name) a'}).values(
    #     'count', 'group__group', 'suite').order_by(
    #     'group__group', 'suite')
    #########################
    # logger.info(api_suite_total.query)
    # union all的字段顺序
    # return suite_total.union(api_suite_total, all=True)
    # 第三版#################
    sql = """select sum(max_count) count, b.`group` `group`, b.suite suite
                from (
                         SELECT (
                                    select case when max(a.n) is null then 1 else max(a.n) end max_count
                                    from (select count(v.param_id) n
                                          from api_case_param p,
                                               api_case_param_values v
                                          where p.id = v.param_id
                                            and p.case_id = c.id
                                          group by p.p_name) a) max_count,
                                c.suite                         suite,
                                g.`group`                       `group`
                         FROM api_case c,
                              api_group g
                         where g.id = c.group_id) b
                where %c1% and %c2%
                group by b.suite, b.`group`"""
    params = []
    c1 = c2 = '1=1'
    if group:
        c1 = 'b.`group` = %s'
        params.append(group)
    if suite:
        c2 = 'b.`suite` = %s'
        params.append(suite)
    sql = sql.replace('%c1%', c1).replace('%c2%', c2)
    api_suite_total = dict_fetch_all(sql, params)
    return list(suite_total) + api_suite_total


def count_api_by_group(group=None, beg=None, end=None):
    # 过滤掉case删除后，case_id为null的记录
    run_his = filter_api_run_his(group=group, beg=beg, end=end).filter(case_id__isnull=False)
    # 非外键下的关联子查询
    # from django.db.models import OuterRef, Subquery
    # groups = ApiGroup.objects.filter(id=OuterRef('group'))
    # case = ApiCase.objects.annotate(grp=groups.values('group')).filter(id=OuterRef('case'))
    # run_his.annotate(group=case.values('grp')).values('group')
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
    # 过滤掉case删除后，case_id为null的记录
    run_his = filter_api_run_his(group=group, beg=beg, end=end).filter(case_id__isnull=False)
    run_his_extra = run_his.annotate(time=Cast(TruncDate('create_time'), output_field=CharField()))
    run_his = run_his_extra.values('result', 'time').annotate(succ=Count('result', Q(result=ResultCode.PASS)),
                                                              fail=Count('result', Q(result=ResultCode.FAIL)),
                                                              error=Count('result', ~Q(result=ResultCode.PASS) & ~Q(
                                                                  result=ResultCode.FAIL)))
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
    pass_count = len(run_his.filter(result=ResultCode.PASS)) + len(api_run_his.filter(result=ResultCode.PASS))
    fail_count = len(run_his.filter(result=ResultCode.FAIL)) + len(api_run_his.filter(result=ResultCode.FAIL))
    error_count = len(run_his.filter(result=ResultCode.ERROR)) + len(
        api_run_his.exclude(result=ResultCode.PASS).exclude(result=ResultCode.FAIL))
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
    run_his = run_his_extra.values('result', 'time').annotate(succ=Count('result', Q(result=ResultCode.PASS)),
                                                              fail=Count('result', Q(result=ResultCode.FAIL)),
                                                              error=Count('result', Q(result=ResultCode.ERROR)))
    logger.info(run_his.query)
    return run_his


def get_group_total():
    group_count = SuiteCount.objects.all().values('group').distinct().count()
    group_count += ApiGroup.objects.all().values('group').distinct().count()
    return group_count


def get_test_total():
    test_total = SuiteCount.objects.all().aggregate(sum=Sum('count'))['sum']
    # api count
    sql = """select sum(b.max_count) count
            from (select (select case when max(a.n) is null then 1 else max(a.n) end max_count
                          from (select count(v.param_id) n
                                from api_case_param p,
                                     api_case_param_values v
                                where p.id = v.param_id
                                  and p.case_id = c.id
                                group by p.p_name) a) max_count
                  FROM api_case c) b"""
    api_test_total = int(raw_sql_fetch_one(sql)[0])
    return test_total + api_test_total


def get_report_total():
    report_total = RunHis.objects.all().values('case').distinct().count()
    report_total += ApiCaseResult.objects.all().count()
    return report_total



