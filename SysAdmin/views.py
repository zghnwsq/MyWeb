from django.http import JsonResponse
# from django.shortcuts import render
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

PARENT_MENU = '系统管理'


# Create your views here.
class NodesV(LoginRequiredMixin, URIPermissionMixin, generic.ListView):
    template_name = 'SysAdmin/nodes.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['expand'] = PARENT_MENU
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
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


@login_required
@auth_check
def stop_node(request):
    ip_port = request.POST.get('ip_port', '#').strip()
    target_node = Node.objects.using('autotest').filter(ip_port__contains=ip_port, status='on')
    if len(target_node) > 0:
        # 防止多次提交
        target_node.update(status='stopping')
        res = stop_node_service(ip_port)
        if 'stopped' in res:
            target_node.update(status='off')
            msg = 'succ'
        else:
            msg = res + '...'
        if 'connection' in res:
            target_node.update(status='off')
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或未启动!'
    return JsonResponse({"msg": msg})


@login_required
@auth_check
def update_node(request):
    ip_port = request.POST.get('ip_port', '#').strip()
    target_node = Node.objects.using('autotest').filter(ip_port__contains=ip_port, status='on')
    if len(target_node) > 0:
        # 防止多次提交
        target_node.update(status='updating')
        res = update_node_service(ip_port)
        if res and 'Starting' in res:
            msg = 'succ'
        else:
            msg = res
        if 'connection' in res:
            target_node.update(status='off')
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或使用中!'
    return JsonResponse({"msg": msg})


@login_required
@auth_check
def del_node(request):
    ip_port = request.POST['ip_port'].strip()
    target_node = Node.objects.using('autotest').filter(ip_port__contains=ip_port, status='off')
    if len(target_node) > 0:
        # 防止多次提交
        target_node.update(status='deleting')
        target_node.delete()
        msg = 'succ'
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或已启动!'
    return JsonResponse({"msg": msg})


class SysConfV(LoginRequiredMixin, URIPermissionMixin, generic.ListView):
    template_name = 'SysAdmin/sys_conf.html'
    context_object_name = 'options'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = get_personal(self.request, context)
        context = get_menu(context)
        context['expand'] = PARENT_MENU
        return context

    def get_queryset(self, **kwargs):
        keys = Sys_Config.objects.values('key').distinct()
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'keys': keys,
            'csrf_token': csrf_token,
        }
        return context


@login_required
@auth_check
def get_sys_conf(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    expand = request.GET.get('expand', 'none')
    key = request.GET.get('key', None)
    desc = request.GET.get('desc', None)
    conf = filter_conf(key=key, desc=desc)
    count = len(conf)
    data_list = paginator(conf, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


@login_required
@auth_check
def modify_sys_conf(request):
    key = request.POST.get('key', None).strip()
    value = request.POST.get('value', None).strip()
    if not key or not value:
        msg = 'Key 或 Value不能为空!'
    else:
        sys_conf = Sys_Config.objects.filter(key=key)
        if len(sys_conf) < 1:
            msg = 'Key 不存在!'
        else:
            sys_conf.update(value=value)
            msg = 'succ'
    return JsonResponse({"msg": msg})






