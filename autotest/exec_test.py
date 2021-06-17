# coding: utf-8
import os
import threading
import time
from threading import ThreadError
from xmlrpc.client import ServerProxy, Binary
from django.db.models import Q
import Utils.zip as zip_util
from MyWeb import settings
from autotest.models import RunHis, Execution, JobQueue, DataSource


def run_by_node(func, mthd, ds_range, node, comment, tester):
    """
    连接节点服务，执行节点测试方法
    :param tester: 执行人
    :param func: 节点注册的方法（一个节点方法对应一个测试类）
    :param mthd: 要执行的测试类中的测试方法,全部（all）或指定
    :param ds_range: 数据源范围, 1  1,3  2-4
    :param node: 节点ip:port
    :param comment: 任务执行备注
    :return: 执行成功将返回:finished,否则返回报错信息
    """
    try:
        s = ServerProxy("http://%s" % node)
        is_alive = s.is_alive()
        if 'alive' not in is_alive:
            raise TimeoutError('Node connection timeout!')
        # 2021.6.4 增加更新数据源
        ds = DataSource.objects.filter(ds_name=func)
        if len(ds) == 1:
            file_path = os.path.join(settings.DATA_SOURCE_ROOT, ds[0].file_path)
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as ds_file:
                    bin_data = Binary(ds_file.read())
                    # print(bin_data)
                    update_ds_func = getattr(s, 'replace_datasource')
                    update_res = update_ds_func(func, bin_data)
                    print(f'Replace datasource result: {update_res}')
                    if 'Error' in update_res:
                        raise Exception(update_res)
        # 2021.5.25 改为通用调用方法
        # func_obj = getattr(s, func)
        func_obj = getattr(s, 'run_suite')
        # res = func_obj(mthd, ds_range, comment, tester)
        res = func_obj({'suite_name': func, 'mtd': mthd, 'rg': ds_range, 'comment': comment, 'tester': tester})
        print(f'RPC return:{res}')
        status = handle_result(s, res)
        return status
    except TimeoutError:
        return 'Node connection timeout!'
    except AttributeError:
        return 'Node function not exists!'
    except ConnectionRefusedError:
        return 'Node connection refused!'
    except Exception as e:
        return f'Node Error: {e.__str__()[:256]}...'


def handle_result(server, res):
    if not isinstance(res, dict):
        return f'Node Error: {res}...'  # 执行成功将返回结果字典,否则返回报错信息
    else:
        # 压缩前文件名或文件夹
        if '.html' in res['report']:
            file_name = res['report'].split(os.sep)[-1]
        else:
            file_name = ''
        file_binary = server.get_report_file(res['report']).data
        time_stamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        # 解压缩文件夹
        report_file_path = os.path.join(os.path.join(settings.BASE_DIR, 'Report'), res['test_group'],
                                        res['test_suite'], time_stamp)
        # zip文件路径
        zip_file_path = report_file_path + '.zip'
        os.makedirs(report_file_path, exist_ok=True)
        # binary数据写入zip
        with open(zip_file_path, 'wb') as handle:
            handle.write(file_binary)
        # 解压缩zip到文件夹
        zip_util.unzip_file(zip_file_path, report_file_path)
        # 写入数据库的相对路径
        op_path = os.path.join(res['test_group'], res['test_suite'], time_stamp, file_name)
        # 写入MyWeb数据库
        his = []
        if len(res['result']) > 0:
            for res in res['result']:
                # print(res)
                his.append(RunHis(group=res['group'], suite=res['suite'], case=res['case'], title=res['title'],
                                  tester=res['tester'], description=res['desc'], comment=res['comment'], report=op_path,
                                  result=res['result'], create_time=res['finish_time']))
            RunHis.objects.bulk_create(his, batch_size=50)
        return 'finished'


class RunnerThread(threading.Thread):
    """
        多线程执行
    """

    def __init__(self, func, mthd, ds_range, node, comment, node_model, tester):
        threading.Thread.__init__(self)
        self.func = func
        self.mthd = mthd
        self.ds_range = ds_range
        self.node = node
        self.comment = comment
        self.node_model = node_model
        self.tester = tester
        self.res = ''

    def run(self):
        self.res = run_by_node(self.func, self.mthd, self.ds_range, self.node, self.comment, self.tester)
        if 'connection' in self.res:
            node_status = 'off'
        else:
            node_status = 'on'
        # 执行结束，释放节点
        for row in self.node_model:
            row.status = node_status
            row.save()
        # 执行结束，修改任务状态
        status = self.res
        print(f'Status:{status}')
        exec_model = Execution.objects.filter(Q(status='running') | Q(status=None), method=self.mthd, func__func=self.func)
        for row in exec_model:
            # row.status = status[:255]
            job = JobQueue.objects.filter(executioin=row.id)
            if job:
                job.update(status='finished')
            row.status = 'finished'
            row.save()

    def get_res(self):
        return self.res


def job_run(func, mthd, ds_range, node, comment, node_model, tester):
    """
    使用多线程，使用节点异步执行测试任务，不阻断页面响应
    :param tester:
    :param func: 节点注册的方法（一个节点方法对应一个测试类）
    :param mthd: 要执行的测试类中的测试方法,全部（all）或指定
    :param ds_range: 数据源范围, 格式如：1  1,3  2-4
    :param node: 节点ip:port
    :param comment: 任务执行备注
    :param node_model: 节点model对象，用于更新状态
    :param tester: 执行人
    :return: none
    """
    thd = RunnerThread(func, mthd, ds_range, node, comment, node_model, tester)
    status = 'running'
    try:
        thd.start()
    except ThreadError:
        status = 'Thread Error'
    finally:
        return status


