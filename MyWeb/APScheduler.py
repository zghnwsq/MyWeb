import datetime
import json
import logging
import socket
# from typing import Union
from typing import Union
from xmlrpc.client import ServerProxy, Transport
from xmlrpc.client import Error
import requests
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
import pytz
from django.db.models import F
from SysAdmin.models import Sys_Config
from autotest.exec_test import job_run
from autotest.models import Node, JobQueue, Execution
from login.models import Weather
from MyWeb import settings
import time
import http.client

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


class TimeoutTransport(Transport):

    timeout = 15  # unit:seconds

    def make_connection(self, host):
        # return an existing connection if possible.  This allows
        # HTTP/1.1 keep-alive.
        if self._connection and host == self._connection[0]:
            return self._connection[1]
        # create a HTTP connection object from a host descriptor
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, http.client.HTTPConnection(chost, timeout=self.timeout)
        return self._connection[1]


def scan_node():
    logger = logging.getLogger('django')
    now = time.strftime('%Y-%m-%d_%H-%M-%S')
    logger.info(f'Scan_node id:{now}: start')
    nodes = Node.objects.all()
    logger.info(f'Scan_node id:{now}: Nodes in list: {nodes}')
    for node in nodes:
        logger.info(f'Scan_node id:{now}: Calling: {node.ip_port}')
        status = 'off'
        try:
            transport = TimeoutTransport()
            s = ServerProxy("http://%s" % node.ip_port, transport=transport)
            is_alive = s.is_alive()
            if 'alive' in is_alive:
                status = 'running' if node.status == 'running' else 'on'
        except Union[TimeoutError, socket.timeout, ConnectionRefusedError, OSError, Error]:
            status = 'off'
        # except socket.timeout:
        #     status = 'off'
        # except ConnectionRefusedError:
        #     status = 'off'
        # except OSError:
        #     status = 'off'
        # except Error:
        #     status = 'off'
        finally:
            logger.info(f'Scan_node id:{now}, Node {node.ip_port} is {status}')
            if status != 'running':
                node.status = status
                node.save()
    logger.info(f'Scan_node id:{now} finished')


def arrange_job():
    logger = logging.getLogger('django')
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    logger.info(f'Arrange_job id:{now}: start')
    jobs = JobQueue.objects.filter(status='new')
    logger.info(f'Arrange_job id:{now}: {len(jobs)} jobs in queue')
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
            logger.info(f'Arrange_job id:{now}: Job {node.id} begin to run, status: {status}')
            # 线程异常，更新任务状态
            if 'Error' in status:
                execution.update(status=status)
        elif len(execution) < 1:
            job.status = 'execution deleted'
            job.save()
    logger.info(f'Arrange_job id:{now}:  finished')


def get_weather():
    logger = logging.getLogger('django')
    logger.info('Get Weather begin')
    edge = datetime.datetime.now() - datetime.timedelta(minutes=30)
    need_refresh = Weather.objects.filter(status='ok', create_time__gte=edge).count() <= 0
    weather = {}
    if need_refresh:
        logger.info('Do get Weather')
        weather_api_key = Sys_Config.objects.get(dict_key='WEATHER_API_KEY').dict_value
        city_location = Sys_Config.objects.get(dict_key='CITY_LOCATION').dict_value
        weather_api_url = Sys_Config.objects.get(dict_key='WEATHER_API_URL').dict_value
        session = requests.session()
        url = f'{weather_api_url}/{weather_api_key}/{city_location}/realtime'
        try:
            response = session.get(url)
            resp_json = json.loads(response.text)
            session.close()
            if 'ok' in resp_json['status']:
                weather['temperature'] = '{:.0f}'.format(resp_json['result']['realtime']['temperature'])
                weather['humidity'] = '{:.0f}'.format(resp_json['result']['realtime']['humidity'] * 100)
                weather['pm25'] = resp_json['result']['realtime']['air_quality']['pm25']
                weather['comfort'] = resp_json['result']['realtime']['life_index']['comfort']['desc']
                skycon = resp_json['result']['realtime']['skycon'].strip()
                weather['skycon'] = settings.skycon_dict[skycon] if skycon in settings.skycon_dict.keys() else skycon
                weather['skycon_icon'] = settings.skycon_icon_dict[
                    skycon] if skycon in settings.skycon_icon_dict.keys() else ''
                weather['aqi'] = resp_json['result']['realtime']['air_quality']['aqi']['chn']
                weather['air_desc'] = resp_json['result']['realtime']['air_quality']['description']['chn']
                Weather.objects.update(status=resp_json['status'].strip(), temperature=weather['temperature'],
                                       humidity=weather['humidity'], pm25=weather['pm25'], comfort=weather['comfort'],
                                       skycon=skycon, aqi=weather['aqi'], air_desc=weather['air_desc'],
                                       create_time=datetime.datetime.now())
            else:
                Weather.objects.update(status=resp_json['status'].strip())
        except requests.exceptions.RequestException:
            session.close()
            Weather.objects.update(status='ng')
    logger.info('Get Weather end')


def start_scheduler():
    logger = logging.getLogger('django')
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults,
                                    timezone=pytz.timezone(settings.TIME_ZONE))
    scheduler.add_job(scan_node, 'interval', id='scan_node', seconds=60, replace_existing=True, max_instances=1,
                      misfire_grace_time=1)
    scheduler.add_job(arrange_job, 'interval', id='arrange_job', seconds=30, replace_existing=True, max_instances=1)
    get_weather_next_run_time = datetime.datetime.now(tz=pytz.timezone(settings.TIME_ZONE)) + datetime.timedelta(
        seconds=5)
    scheduler.add_job(get_weather, 'interval', id='get_weather',
                      next_run_time=get_weather_next_run_time, seconds=1800, replace_existing=True, max_instances=1)
    logger.info('scheduler start')
    scheduler.start()
