import datetime
# from django.db.models import Min, Count, CharField, F
# from django.db.models.functions import TruncDate, Cast
# import copy
from autotest.models import Node
from .models import Sys_Config


def filter_nodes(tag=None, status=None, ip_port=None):
    nodes = Node.objects.all().order_by('-status').values('tag', 'status', 'ip_port')
    if tag:
        nodes = nodes.filter(tag__contains=tag)
    if status:
        nodes = nodes.filter(status=status)
    if ip_port:
        nodes = nodes.filter(ip_port__contains=ip_port)
    return nodes


def filter_conf(key=None, desc=None):
    conf = Sys_Config.objects.all().values('dict_key', 'dict_value', 'description')
    if key:
        conf = conf.filter(dict_key=key)
    if desc:
        conf = conf.filter(description=desc)
    return conf








