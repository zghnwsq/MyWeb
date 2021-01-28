from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from SysAdmin.node_manage import *
from SysAdmin.orm import *
from Utils.MyMixin import URIPermissionMixin
from django.views import generic
from Utils.Paginator import paginator
from Utils.Personal import get_personal, get_menu
from Utils.decorators import auth_check
from autotest.models import Node


# Create your views here.
class NodesV(LoginRequiredMixin, URIPermissionMixin, generic.ListView):
    template_name = 'SysAdmin/nodes.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['expand'] = '系统管理'
        return context

    def get_queryset(self, **kwargs):
        tags = Node.objects.using('autotest').values('tag').distinct()
        status = Node.objects.using('autotest').values('status').distinct()
        ip_port = Node.objects.using('autotest').values('ip_port').distinct()
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'tags': tags,
            'status': status,
            'ip_port': ip_port,
            'csrf_token': csrf_token,
        }
        return context


@login_required
@auth_check
def get_nodes(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    expand = request.GET.get('expand', 'none')
    nodes = filter_nodes(
        tag=request.GET.get('tag', None),
        status=request.GET.get('status', None),
        ip_port=request.GET.get('ip_port', None)
    )
    count = len(nodes)
    data_list = paginator(nodes, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list, "expand": expand})


@login_required
@auth_check
def stop_node(request):
    ip_port = request.POST['ip_port'].strip()
    target_node = Node.objects.using('autotest').filter(ip_port__contains=ip_port, status='on')
    if len(target_node) > 0:
        res = stop_node_service(ip_port)
        if 'stopped' in res:
            target_node.update(status='off')
            msg = 'succ'
        else:
            msg = res[:32] + '...'
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或未启动!'
    return JsonResponse({"msg": msg})


@login_required
@auth_check
def update_node(request):
    ip_port = request.POST['ip_port'].strip()
    target_node = Node.objects.using('autotest').filter(ip_port__contains=ip_port, status='on')
    if len(target_node) > 0:
        res = update_node_service(ip_port)
        if res and 'Starting' in res:
            msg = 'succ'
        else:
            msg = res
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或使用中!'
    return JsonResponse({"msg": msg})


@login_required
@auth_check
def del_node(request):
    ip_port = request.POST['ip_port'].strip()
    target_node = Node.objects.using('autotest').filter(ip_port__contains=ip_port, status='off')
    if len(target_node) > 0:
        target_node.delete()
        msg = 'succ'
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或已启动!'
    return JsonResponse({"msg": msg})






