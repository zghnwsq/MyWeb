from django.contrib.sessions.models import Session
from django.utils import timezone

from login.models import UserMenu, Menu
from django.contrib.auth.models import User


def get_personal(request, context):
    user_name = request.session['user_name']
    user_group = request.session['user_group']
    context['user_name'] = user_name
    context['user_group'] = user_group
    context['message'] = ''
    return context


def get_menu(context):
    user = User.objects.get(username=context['user_name'])
    all_menu = UserMenu.objects.filter(user=user).values('menu')
    first_level = Menu.objects.filter(id__in=all_menu, parent__isnull=True).order_by('list_order')
    u_menu = []
    for m1 in first_level:
        menu_items = {'url': m1.url, 'text': m1.text}
        second_level = Menu.objects.filter(id__in=all_menu, parent=m1.id).order_by('list_order')
        childs = []
        for m2 in second_level:
            childs.append({'url': m2.url, 'text': m2.text})
        menu_items['childs'] = childs
        u_menu.append(menu_items)
    context['menus'] = u_menu
    return context


def clear_logged_session(user):
    valid_session_obj_list = Session.objects.filter(expire_date__gt=timezone.now())
    logged_user_list = []
    for session_obj in valid_session_obj_list:
        user_id = session_obj.get_decoded().get("_auth_user_id")
        logged_user_list.append({'id': user_id, 'session_obj': session_obj})
    # this_user = User.objects.get(username=user.username)
    for logged_user in logged_user_list:
        if str(user.id) == logged_user['id']:
            logged_user['session_obj'].delete()
