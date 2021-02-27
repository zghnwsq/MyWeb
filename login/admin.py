from django.contrib import admin

# Register your models here.
from login.models import Menu, UserMenu, UserPermission, PermissionDict


class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'url', 'parent', 'list_order')


class UserMenuAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu')
    fieldsets = [
        ('user_menu', {'fields': ['user', 'menu']}),
    ]


class PermissionDictAdmin(admin.ModelAdmin):
    list_display = ('permi', 'text')


class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'permi')
    fieldsets = [
        ('user_permission', {'fields': ['user', 'permi']}),
    ]


admin.site.register(Menu, MenuAdmin)
admin.site.register(UserMenu, UserMenuAdmin)
admin.site.register(PermissionDict, PermissionDictAdmin)
admin.site.register(UserPermission, UserPermissionAdmin)


