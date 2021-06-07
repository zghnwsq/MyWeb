import logging
from xmlrpc.client import ServerProxy
from xmlrpc.client import Error
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from django.db.models import F
from .exec_test import job_run
from .models import Node, JobQueue, Execution
from MyWeb import settings
import time

jobstores = {
    'default': MemoryJobStore()
}
executors = {
    'default': ThreadPoolExecutor(5),
    # 'processpool': ProcessPoolExecutor(1)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 1
}


def scan_node():
    logger = logging.getLogger('django')
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'{now} run scan_node')
    nodes = Node.objects.all()
    logger.info(f'Nodes in list: {nodes}')
    for node in nodes:
        logger.info(f'Calling: {node.ip_port}')
        status = 'off'
        try:
            s = ServerProxy("http://%s" % node.ip_port)
            is_alive = s.is_alive()
            if 'alive' in is_alive:
                status = 'on' if node.status != 'running' else 'running'
        except TimeoutError:
            status = 'off'
        except ConnectionRefusedError:
            status = 'off'
        except Error:
            status = 'off'
        finally:
            logger.info(f'Node {node.ip_port} is {status}')
            node.status = status
            node.save()
    logger.info(f'Scan_node@{now} finished')


def arrange_job():
    logger = logging.getLogger('django')
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'{now} run arrange_job')
    jobs = JobQueue.objects.filter(status='new')
    logger.info(f'{len(jobs)} jobs in queue')
    for job in jobs:
        node = Node.objects.get(ip_port__contains=job.node)
        execution = Execution.objects.filter(jobqueue=job).values('func__func', 'method', 'ds_range', 'comment',
                                                                  'status').annotate(func=F('func__func'))
        if node and node.status == 'on' and len(execution) > 0:
            node.status = 'running'
            node.save()
            execution.update(status='running')
            job.status = 'running'
            job.save()
            # execution:qurey set, node: qurey set或list
            status = job_run(execution[0]['func'], execution[0]['method'], execution[0]['ds_range'], job.node,
                             execution[0]['comment'], [node], job.tester)
            logger.info(f'Job {node.id} begin to run, status: {status}')
            # 线程异常，更新任务状态
            if 'Error' in status:
                execution.update(status=status)
        elif len(execution) < 1:
            job.status = 'execution deleted'
            job.save()
    logger.info(f'Arrange_job@{now} finished')


def start_scheduler():
    logger = logging.getLogger('django')
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
                                    timezone=pytz.timezone(settings.TIME_ZONE))
    scheduler.add_job(scan_node, 'interval', id='scan_node', seconds=60, replace_existing=True, max_instances=1,
                      misfire_grace_time=1)
    scheduler.add_job(arrange_job, 'interval', id='arrange_job', seconds=30, replace_existing=True, max_instances=1)
    logger.info('scheduler start')
    scheduler.start()




