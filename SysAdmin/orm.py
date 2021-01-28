import datetime
from django.db.models import Min, Count, CharField, F
from django.db.models.functions import TruncDate, Cast
import copy
from autotest.models import Node


def filter_nodes(tag=None, status=None, ip_port=None):
    nodes = Node.objects.using('autotest').all().order_by('-status').values('tag', 'status', 'ip_port')
    if tag:
        nodes = nodes.filter(tag__contains=tag)
    if status:
        nodes = nodes.filter(status=status)
    if ip_port:
        nodes = nodes.filter(ip_port__contains=ip_port)
    return nodes










