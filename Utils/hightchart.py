# coding=utf-8
from Utils.Constant import ResultCode


def group_count_and_result_series(run_his):
    series = []
    names = run_his.values('group').distinct()
    for name in names:
        list_of_group = run_his.filter(group=name['group']).order_by('time')
        datas, pass_datas, fail_datas = {}, {}, {}
        pass_of_group = list_of_group.filter(result=ResultCode.PASS)
        fail_of_group = list_of_group.exclude(result=ResultCode.PASS).exclude(result=ResultCode.ERROR)
        for data_of_group in list_of_group:
            datas[data_of_group['time']] = data_of_group['count']
        series.append({'name': name['group'], 'data': datas})
        for ps in pass_of_group:
            pass_datas[ps['time']] = ps['count']
        series.append({'name': name['group'] + '_pass', 'data': pass_datas})
        for fa in fail_of_group:
            fail_datas[fa['time']] = fa['count']
        series.append({'name': name['group'] + '_fail', 'data': fail_datas})
    return series


def group_count_series(run_his):
    series = []
    names = run_his.values('group').distinct()
    for name in names:
        list_of_group = run_his.filter(group=name['group']).order_by('time')
        datas = []
        for data_of_group in list_of_group:
            datas.append([data_of_group['time'], data_of_group['count']])
        series.append({'name': name['group'], 'data': datas})
    return series


def result_count_series(run_his):
    """
        按执行结果、日期统计次数
    :param run_his: count_by_result结果
    :return: 面积图数据
    """
    succ, fail, error = {}, {}, {}
    for item in run_his:
        # 日期没有对应类型则填充0
        succ[item['time']] = item['succ'] or (succ[item['time']] if item['time'] in succ else 0)
        fail[item['time']] = item['fail'] or (fail[item['time']] if item['time'] in fail else 0)
        error[item['time']] = item['error'] or (error[item['time']] if item['time'] in error else 0)
    summary = [
        {'name': '成功', 'data': succ},
        {'name': '失败', 'data': fail},
        {'name': '错误', 'data': error},
    ]
    return summary





