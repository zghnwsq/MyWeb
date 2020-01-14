from django.contrib import admin

# Register your models here.
from login.models import Menu, UserMenu


class MenuAdmin(admin.ModelAdmin):
    list_display = ('text', 'url', 'parent', 'order')


class UserMenuAdmin(admin.ModelAdmin):
    # list_display = ('user', 'menu')
    fieldsets = [
        ('user', {'fields': ['user']}),
        (None, {'fields': ['menu']}),
    ]


admin.site.register(Menu, MenuAdmin)
# admin.site.register(UserMenu, UserMenuAdmin)

