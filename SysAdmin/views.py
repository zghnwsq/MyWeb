import json
from django.http import JsonResponse
# from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from SysAdmin.node_manage import *
from SysAdmin.orm import *
from Utils.MyMixin import URIPermissionMixin
# from django.views import generic
from Utils.Paginator import paginator
from Utils.Personal import get_personal
from Utils.decorators import auth_check
from Utils.CustomView import ListViewWithMenu
from autotest.models import Node

PARENT_MENU = '系统管理'


# Create your views here.
class NodesV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'SysAdmin/nodes.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context = get_personal(self.request, context)
    #     context['menus'] = self.request.session.get('menus', [])
    #     context['expand'] = PARENT_MENU
    #     return context

    def get_queryset(self, **kwargs):
        tags = Node.objects.values('tag').distinct()
        status = Node.objects.values('status').distinct()
        ip_port = Node.objects.values('ip_port').distinct()
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'tags': tags,
            'status': status,
            'ip_port': ip_port,
            'csrf_token': csrf_token,
        }
        return context


@auth_check
@login_required
def get_nodes(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    # expand = request.GET.get('expand', 'none')
    nodes = filter_nodes(
        tag=request.GET.get('tag', None),
        status=request.GET.get('status', None),
        ip_port=request.GET.get('ip_port', None)
    )
    count = len(nodes)
    data_list = paginator(nodes, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


@auth_check
@login_required
def stop_node(request):
    req = json.loads(request.body)
    ip_port = req.get('ip_port', '#').strip()
    target_node = Node.objects.filter(ip_port__contains=ip_port, status='on')
    if len(target_node) > 0:
        # 防止多次提交
        target_node.update(status='stopping')
        res = stop_node_service(ip_port)
        if 'stopped' in res:
            Node.objects.filter(ip_port__contains=ip_port, status='stopping').update(status='off')
            msg = 'succ'
        else:
            msg = res + '...'
        if 'connection' in res:
            Node.objects.filter(ip_port__contains=ip_port, status='stopping').update(status='off')
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或未启动!'
    return JsonResponse({"msg": msg})


@auth_check
@login_required
@require_http_methods(['POST'])
def update_node(request):
    req = json.loads(request.body)
    ip_port = req.get('ip_port', '#').strip()
    target_node = Node.objects.filter(ip_port__contains=ip_port, status='on')
    if len(target_node) > 0:
        # 防止多次提交
        target_node.update(status='updating')
        res = update_node_service(ip_port)
        if res and 'Starting' in res:
            msg = 'succ'
        else:
            msg = res
        if 'connection' in res:
            Node.objects.filter(ip_port__contains=ip_port, status='updating').update(status='off')
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或使用中!'
    return JsonResponse({"msg": msg})


@auth_check
@login_required
@require_http_methods(['POST'])
def del_node(request):
    req = json.loads(request.body)
    ip_port = req.get('ip_port', '#').strip()
    target_node = Node.objects.filter(ip_port__contains=ip_port, status='off')
    if len(target_node) > 0:
        # 防止多次提交
        target_node.update(status='deleting')
        Node.objects.filter(ip_port__contains=ip_port, status='deleting').delete()
        msg = 'succ'
    else:
        msg = f'Error: 该节点 {ip_port} 不存在或已启动!'
    return JsonResponse({"msg": msg})


class SysConfV(LoginRequiredMixin, URIPermissionMixin, ListViewWithMenu):
    template_name = 'SysAdmin/sys_conf.html'
    context_object_name = 'options'
    parent_menu = PARENT_MENU

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context = get_personal(self.request, context)
    #     context['menus'] = self.request.session.get('menus', [])
    #     context['expand'] = PARENT_MENU
    #     return context

    def get_queryset(self, **kwargs):
        keys = Sys_Config.objects.values('dict_key').distinct()
        csrf_token = self.request.COOKIES.get('csrftoken')
        context = {
            'keys': keys,
            'csrf_token': csrf_token,
        }
        return context


@auth_check
@login_required
def get_sys_conf(request):
    page = request.GET.get('page', '0')
    limit = request.GET.get('limit', '30')
    # expand = request.GET.get('expand', 'none')
    key = request.GET.get('key', None)
    desc = request.GET.get('desc', None)
    conf = filter_conf(key=key, desc=desc)
    count = len(conf)
    data_list = paginator(conf, int(page), int(limit))
    return JsonResponse({"code": 0, "msg": "", "count": count, "data": data_list})


@login_required
@auth_check
@require_http_methods(['POST'])
def modify_sys_conf(request):
    req = json.loads(request.body)
    key = req.get('key', None).strip()
    value = req.get('value', None).strip()
    if not key or not value:
        msg = 'Key 或 Value不能为空!'
    else:
        sys_conf = Sys_Config.objects.filter(dict_key=key)
        if len(sys_conf) < 1:
            msg = 'Key 不存在!'
        else:
            sys_conf.update(dict_value=value)
            msg = 'succ'
    return JsonResponse({"msg": msg})






