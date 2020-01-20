from django.contrib import admin

# Register your models here.
from login.models import Menu, UserMenu


class MenuAdmin(admin.ModelAdmin):
    list_display = ('id', 'text', 'url', 'parent', 'order')


class UserMenuAdmin(admin.ModelAdmin):
    list_display = ('user', 'menu')
    fieldsets = [
        ('user_menu', {'fields': ['user', 'menu']}),
    ]


admin.site.register(Menu, MenuAdmin)
admin.site.register(UserMenu, UserMenuAdmin)

