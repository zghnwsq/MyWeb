# coding: utf-8
import threading
from threading import ThreadError
from xmlrpc.client import ServerProxy


def run_by_node(func, mthd, ds_range, node, comment):
    """
    连接节点服务，执行节点测试方法
    :param func: 节点注册的方法（一个节点方法对应一个测试类）
    :param mthd: 要执行的测试类中的测试方法,全部（all）或指定
    :param ds_range: 数据源范围, 1  1,3  2-4
    :param node: 节点ip:port
    :param comment: 任务执行备注
    :return: 执行成功将返回:finished,否则返回报错信息
    """
    try:
        s = ServerProxy("http://%s" % node)
        func_obj = getattr(s, func)
        res = func_obj(mthd, ds_range, comment)
        return res  # 执行成功将返回:finished,否则返回报错信息
    except TimeoutError:
        return 'Node connection timeout!'
    except AttributeError:
        return 'Node function not exists!'


class RunnerThread(threading.Thread):
    """
        多线程执行
    """

    def __init__(self, func, mthd, ds_range, node, comment, node_model, exec_model):
        threading.Thread.__init__(self)
        self.func = func
        self.mthd = mthd
        self.ds_range = ds_range
        self.node = node
        self.comment = comment
        self.node_model = node_model
        self.exec_model = exec_model
        self.res = ''

    def run(self):
        self.res = run_by_node(self.func, self.mthd, self.ds_range, self.node, self.comment)
        # 执行结束，释放节点
        for row in self.node_model:
            row.status = 'on'
            row.save()
        # 执行结束，修改任务状态
        status = self.res
        for row in self.exec_model:
            row.status = status
            row.save()

    def get_res(self):
        return self.res


def job_run(func, mthd, ds_range, node, comment, node_model, exec_model):
    """
    使用多线程，使用节点异步执行测试任务，不阻断页面响应
    :param func: 节点注册的方法（一个节点方法对应一个测试类）
    :param mthd: 要执行的测试类中的测试方法,全部（all）或指定
    :param ds_range: 数据源范围, 1  1,3  2-4
    :param node: 节点ip:port
    :param comment: 任务执行备注
    :param node_model: 节点model对象，用于更新状态
    :param exec_model: 任务model对象，用于更新状态
    :return: none
    """
    thd = RunnerThread(func, mthd, ds_range, node, comment, node_model, exec_model)
    status = 'running'
    try:
        thd.start()
    except ThreadError:
        status = 'Thread Error'
    finally:
        return status

