from login.models import UserMenu, Menu
from django.contrib.auth.models import Group, User


def get_personal(request, context):
    user_name = request.session['user_name']
    user_group = request.session['user_group']
    context['user_name'] = user_name
    context['user_group'] = user_group
    return context


def get_menu(context):
    user = User.objects.get(username=context['user_name'])
    all_menu = UserMenu.objects.filter(user=user).values('menu')
    first_level = Menu.objects.filter(id__in=all_menu, parent__isnull=True).order_by('order')
    u_menu = []
    for m1 in first_level:
        menu_items = {'url': m1.url, 'text': m1.text}
        second_level = Menu.objects.filter(id__in=all_menu, parent=m1.id).order_by('order')
        childs = []
        for m2 in second_level:
            childs.append({'url': m2.url, 'text': m2.text})
        menu_items['childs'] = childs
        u_menu.append(menu_items)
    context['menus'] = u_menu
    return context
