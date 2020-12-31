# coding=utf-8

def chart_series(run_his):
    series = []
    names = run_his.values('group').distinct()
    for name in names:
        list_of_group = run_his.filter(group=name['group'])
        datas = []
        pass_datas = []
        fail_datas = []
        pass_of_group = list_of_group.filter(result='0')
        fail_of_group = list_of_group.exclude(result='0').exclude(result='3')
        for data_of_group in list_of_group:
            datas.append([data_of_group['time'], data_of_group['count']])
        series.append({'name': name['group'], 'data': datas})
        for ps in pass_of_group:
            pass_datas.append([ps['time'], ps['count']])
        series.append({'name': name['group'] + '_pass', 'data': pass_datas})
        for fa in fail_of_group:
            fail_datas.append([fa['time'], fa['count']])
        series.append({'name': name['group'] + '_fail', 'data': fail_datas})
    return series
