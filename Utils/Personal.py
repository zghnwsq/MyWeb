from django.contrib.sessions.models import Session
# from django.shortcuts import render
from django.utils import timezone
from login.models import UserMenu, Menu
from django.contrib.auth.models import Group


def get_personal(request, context):
    if 'user_name' in request.session.keys() and 'user_group' in request.session.keys():
        user_name = request.session['user_name']
        user_group = request.session['user_group']
        context['user_name'] = user_name
        context['user_group'] = user_group
        # context['message'] = ''
    else:
        user_name = request.user.username
        user_group = Group.objects.filter(user__username=request.user.username)[0].name
        request.session['user_name'] = user_name
        request.session['user_group'] = user_group
        context['user_name'] = user_name
        context['user_group'] = user_group
    return context


def _get_user_menu(user_menu, parent=None, parent_isnull=True):
    if parent:
        this_level = Menu.objects.filter(id__in=user_menu, parent=parent).order_by('list_order')
    else:
        this_level = Menu.objects.filter(id__in=user_menu, parent__isnull=parent_isnull).order_by('list_order')
    menus = []
    for m in this_level:
        m_items = {'url': m.url, 'text': m.text, 'icon': m.icon, 'childs': _get_user_menu(user_menu, m.id)}
        menus.append(m_items)
    return menus


def get_menu(context):
    # user = User.objects.get(username=context['user_name'])
    # 2021.5.16 优化逻辑,使用递归,后台不限制层级数
    all_menu = UserMenu.objects.filter(user__username=context['user_name']).values('menu')
    u_menu = _get_user_menu(all_menu)
    # first_level = Menu.objects.filter(id__in=all_menu, parent__isnull=True).order_by('list_order')
    # u_menu = []
    # for m1 in first_level:
    #     menu_items = {'url': m1.url, 'text': m1.text, 'icon': m1.icon}
    #     second_level = Menu.objects.filter(id__in=all_menu, parent=m1.id).order_by('list_order')
    #     childs = []
    #     for m2 in second_level:
    #         childs.append({'url': m2.url, 'text': m2.text, 'icon': m2.icon})
    #     menu_items['childs'] = childs
    #     u_menu.append(menu_items)
    # 2021.4.2 user menu改为存储在session中
    # context['menus'] = u_menu
    return u_menu


def clear_logged_session(user):
    # 废弃
    valid_session_obj_list = Session.objects.filter(expire_date__gt=timezone.now())
    logged_user_list = []
    for session_obj in valid_session_obj_list:
        user_id = session_obj.get_decoded().get("_auth_user_id")
        logged_user_list.append({'id': user_id, 'session_obj': session_obj})
    # this_user = User.objects.get(username=user.username)
    for logged_user in logged_user_list:
        if str(user.id) == logged_user['id']:
            logged_user['session_obj'].delete()
